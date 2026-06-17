import time
import random
import requests
from typing import Optional, Tuple, Dict, Any
from datetime import timedelta, datetime

from decouple import config
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from geopy.geocoders import Nominatim

from matchfinder.models import Sport, Event


class Command(BaseCommand):
    help = "Fetches real matches (Football, Rugby) via the API-Sports ecosystem and populates the database."

    # Class-level configuration for easy maintenance
    SPORTS_CONFIG = [
        {
            "name": "Football",
            "slug": "football",
            "url": "https://v3.football.api-sports.io/fixtures",
            "leagues": [61, 62, 63],
            "season": 2024
        },
        {
            "name": "Rugby",
            "slug": "rugby",
            "url": "https://v1.rugby.api-sports.io/games",
            "leagues": [16, 17],
            "season": 2024
        }
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geocoder = Nominatim(user_agent="matchfinder_app")
        # In-memory cache to prevent redundant API calls to OpenStreetMap
        self.location_cache: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
        self.total_created = 0
        self.total_updated = 0

    def handle(self, *args, **options):
        """Main entry point for the Django management command."""
        api_key = config('API_KEY_API_SPORTS')
        headers = {"x-apisports-key": api_key}

        for sport_data in self.SPORTS_CONFIG:
            sport_obj, _ = Sport.objects.get_or_create(
                name=sport_data["name"],
                defaults={'slug': sport_data["slug"]}
            )

            for league_id in sport_data["leagues"]:
                self._fetch_and_process_league(sport_data, league_id, sport_obj, headers)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nProcess completed! Summary: {self.total_created} created, {self.total_updated} updated."
            )
        )

    def _fetch_and_process_league(self, sport_data: Dict[str, Any], league_id: int, sport_obj: Sport, headers: Dict[str, str]) -> None:
        """Fetches matches for a specific league and triggers the processing pipeline."""
        url = f"{sport_data['url']}?league={league_id}&season={sport_data['season']}"
        self.stdout.write(f"\n[+] Querying {sport_data['name']} API (League {league_id})...")

        try:
            # Added a timeout to prevent the command from hanging indefinitely
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() 
            data = response.json()

            if data.get("errors"):
                self.stdout.write(self.style.ERROR(f"API-Sports Error: {data.get('errors')}"))
                return

            matches = data.get("response", [])
            self.stdout.write(f" -> {len(matches)} matches found.")

            for item in matches:
                self._process_single_match(item, sport_obj, sport_data['slug'])

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"API Request failed: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error during league processing: {e}"))
        finally:
            # Ensure the rate limit pause is always respected, even if an error occurs
            time.sleep(1.5)

    def _process_single_match(self, item: Dict[str, Any], sport_obj: Sport, sport_slug: str) -> None:
        """Parses raw match data and updates/creates the Event in the database."""
        fixture_data = item.get("fixture") or item
        external_id = f"{sport_slug}_{fixture_data.get('id')}"

        # 1. Date Processing
        raw_date_str = fixture_data.get("date")
        if not raw_date_str:
            return
        
        raw_date = parse_datetime(raw_date_str)
        if not raw_date:
            return

        start_time = self._generate_mock_future_date(raw_date)

        # 2. Venue Processing
        venue_name, venue_city, venue_image = self._parse_venue(fixture_data.get("venue"), sport_slug)

        # 3. Geocoding
        lat, lon = self._get_coordinates(venue_name, venue_city)

        # 4. Team and League Extraction
        teams = item.get("teams", {})
        home_team = teams.get("home", {}).get("name") or "Home Team"
        away_team = teams.get("away", {}).get("name") or "Away Team"
        title = f"{home_team} vs {away_team}"
        
        league_name = item.get("league", {}).get("name") or "Unknown Competition"

        # 5. Database Persistence
        event, created = Event.objects.update_or_create(
            external_api_id=external_id,
            defaults={
                'title': title,
                'sport': sport_obj,
                'league_name': league_name,
                'venue_image': venue_image,
                'latitude': lat,
                'longitude': lon,
                'start_time': start_time,
                'venue_name': venue_name,
                'city': venue_city,
                'price': 'See ticketing',
            }
        )

        if created:
            self.total_created += 1
        else:
            self.total_updated += 1

    def _generate_mock_future_date(self, original_date: datetime) -> datetime:
        """MVP Hack: Shifts a past date to a random future date (0-45 days) while preserving the original time."""
        now = timezone.now()
        days_to_add = random.randint(0, 45)
        future_date = now + timedelta(days=days_to_add)
        
        try:
            return future_date.replace(
                hour=original_date.hour, 
                minute=original_date.minute, 
                second=0, 
                microsecond=0
            )
        except ValueError:
            return future_date

    def _parse_venue(self, venue_data: Any, sport_slug: str) -> Tuple[str, str, str]:
        """Extracts venue details and generates an image URL if applicable."""
        if not venue_data or isinstance(venue_data, str):
            return (venue_data or "TBD Stadium", "Unknown City", "")

        venue_name = venue_data.get("name") or "TBD Stadium"
        venue_city = venue_data.get("city") or "Unknown City"
        venue_id = venue_data.get("id")
        
        venue_image = f"https://media.api-sports.io/{sport_slug}/venues/{venue_id}.png" if venue_id else ""
        
        return venue_name, venue_city, venue_image

    def _get_coordinates(self, venue_name: str, city: str) -> Tuple[Optional[float], Optional[float]]:
        """Fetches GPS coordinates via Nominatim, utilizing an in-memory cache to save quotas."""
        cache_key = f"{venue_name}_{city}"
        
        if cache_key in self.location_cache:
            return self.location_cache[cache_key]

        lat, lon = None, None
        try:
            # Strictly respect OpenStreetMap's usage policy (1 request per second)
            time.sleep(1)
            
            location = None
            # 1. Attempt precise stadium geocoding
            if venue_name and venue_name != "TBD Stadium":
                query = f"{venue_name}, {city}, France"
                location = self.geocoder.geocode(query, timeout=5)
            
            # 2. Fallback to city geocoding if stadium is missing or not found
            if not location:
                query_city = f"{city}, France"
                location = self.geocoder.geocode(query_city, timeout=5)

            if location:
                lat, lon = location.latitude, location.longitude

        except Exception as e:
            # Log the exception but do not crash the script over a geocoding failure
            self.stdout.write(self.style.WARNING(f"Geocoding failed for {cache_key}: {e}"))

        # Save to cache even if None, to prevent retrying a failed location
        self.location_cache[cache_key] = (lat, lon)
        return lat, lon