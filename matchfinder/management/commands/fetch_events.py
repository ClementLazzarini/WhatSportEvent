import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from matchfinder.models import Sport, Event
from decouple import config

class Command(BaseCommand):
    help = "Récupère tous les matchs d'une saison de football via API-Football"

    def handle(self, *args, **kwargs):
        api_key = config('API_KEY_API_SPORTS')
        headers = {
            "x-apisports-key": api_key
        }

        sport_foot, _ = Sport.objects.get_or_create(name="Football", defaults={'slug': 'football'})


        league_id = 61 
        season = 2024

        url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"
        
        self.stdout.write(f"Interrogation de l'API pour la ligue {league_id} (saison {season})...")
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Erreur API : {response.status_code}"))
                return

            data = response.json()

            api_errors = data.get("errors")
            if api_errors:
                self.stdout.write(self.style.ERROR(f"Erreur API-Football : {api_errors}"))
                return
            
            matches = data.get("response", [])
            
            self.stdout.write(f"{len(matches)} matchs trouvés. Enregistrement en base de données...")

            events_created = 0
            events_updated = 0

            for item in matches:
                fixture = item.get("fixture", {})
                teams = item.get("teams", {})
                
                venue_data = fixture.get("venue") or {}
                venue_name = venue_data.get("name") or "Stade à définir"
                venue_city = venue_data.get("city") or "Ville inconnue"

                title = f"{teams.get('home', {}).get('name')} vs {teams.get('away', {}).get('name')}"
                external_id = str(fixture.get("id"))

                raw_date = parse_datetime(fixture.get("date"))
                if is_naive(raw_date):
                    start_time = make_aware(raw_date)
                else:
                    start_time = raw_date

                event, created = Event.objects.update_or_create(
                    external_api_id=external_id,
                    defaults={
                        'title': title,
                        'sport': sport_foot,
                        'start_time': start_time,
                        'venue_name': venue_name,
                        'city': venue_city,
                        'price': 'Voir billetterie',
                    }
                )

                if created:
                    events_created += 1
                else:
                    events_updated += 1

            self.stdout.write(self.style.SUCCESS(f"Importation terminée ! {events_created} matchs créés, {events_updated} mis à jour."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Une erreur est survenue dans le script : {e}"))