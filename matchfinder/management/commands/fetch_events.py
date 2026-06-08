import time
import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from matchfinder.models import Sport, Event
from decouple import config

class Command(BaseCommand):
    help = "Récupère les matchs réels (Foot, Rugby, Basket) via l'écosystème API-Sports"

    def handle(self, *args, **kwargs):
        api_key = config('API_KEY_API_SPORTS')
        headers = {
            "x-apisports-key": api_key
        }

        # Configuration des requêtes par sport
        # Tu peux facilement ajouter/retirer des ligues ici
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

        total_created = 0
        total_updated = 0

        for sport_data in SPORTS_CONFIG:
            # 1. On s'assure que le sport existe en base
            sport_obj, _ = Sport.objects.get_or_create(
                name=sport_data["name"], 
                defaults={'slug': sport_data["slug"]}
            )

            for league_id in sport_data["leagues"]:
                url = f"{sport_data['url']}?league={league_id}&season={sport_data['season']}"
                self.stdout.write(f"\n[+] Interrogation API {sport_data['name']} (Ligue {league_id})...")

                try:
                    response = requests.get(url, headers=headers)
                    
                    if response.status_code != 200:
                        self.stdout.write(self.style.ERROR(f"Erreur API ({response.status_code})"))
                        continue

                    data = response.json()
                    
                    if data.get("errors"):
                        self.stdout.write(self.style.ERROR(f"Erreur API-Sports : {data.get('errors')}"))
                        continue
                    
                    matches = data.get("response", [])
                    self.stdout.write(f" -> {len(matches)} matchs trouvés.")

                    for item in matches:
                        fixture_data = item.get("fixture") or item
                        
                        external_id = f"{sport_data['slug']}_{fixture_data.get('id')}"

                        # Gestion de la date
                        raw_date = parse_datetime(fixture_data.get("date"))
                        if not raw_date:
                            continue
                            
                        if is_naive(raw_date):
                            start_time = make_aware(raw_date)
                        else:
                            start_time = raw_date

                        venue_data = fixture_data.get("venue") or {}
                        if isinstance(venue_data, str):
                            venue_name = venue_data
                            venue_city = "Ville inconnue"
                        else:
                            venue_name = venue_data.get("name") or "Stade à définir"
                            venue_city = venue_data.get("city") or "Ville inconnue"

                        # Gestion des équipes
                        teams = item.get("teams", {})
                        home_team = teams.get("home", {}).get("name") or "Équipe Domicile"
                        away_team = teams.get("away", {}).get("name") or "Équipe Extérieur"
                        title = f"{home_team} vs {away_team}"
                        league_info = item.get("league", {})
                        league_name = league_info.get("name") or "Compétition"

                        # 3. Enregistrement en base
                        event, created = Event.objects.update_or_create(
                            external_api_id=external_id,
                            defaults={
                                'title': title,
                                'sport': sport_obj,
                                'league_name': league_name,
                                'start_time': start_time,
                                'venue_name': venue_name,
                                'city': venue_city,
                                'price': 'Voir billetterie',
                            }
                        )

                        if created:
                            total_created += 1
                        else:
                            total_updated += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Exception lors du traitement : {e}"))
                
                # Pause de 1.5 secondes pour respecter le Rate Limit de l'API gratuite (max 10 req/minute)
                time.sleep(1.5)

        self.stdout.write(self.style.SUCCESS(f"\nTerminé ! Bilan : {total_created} créés, {total_updated} mis à jour."))