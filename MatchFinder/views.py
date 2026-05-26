from django.shortcuts import render

def home_view(request):
    # Fausse donnée pour créer l'interface (Mocking)
    dummy_events = [
        {
            'title': 'Stade Toulousain vs La Rochelle',
            'sport': 'Rugby',
            'date': '24 Mai 2026 - 21h00',
            'venue': 'Stade Ernest-Wallon, Toulouse',
            'price': 'À partir de 25€',
            'tag_color': 'bg-red-100 text-red-800'
        },
        {
            'title': 'Tournoi de Baseball Amateur',
            'sport': 'Baseball',
            'date': '25 Mai 2026 - 14h00',
            'venue': 'Stade des Argoulets, Toulouse',
            'price': 'Gratuit',
            'tag_color': 'bg-blue-100 text-blue-800'
        },
        {
            'title': 'Téfécé vs Olympique de Marseille',
            'sport': 'Football',
            'date': '30 Mai 2026 - 20h00',
            'venue': 'Stadium de Toulouse',
            'price': 'À partir de 35€',
            'tag_color': 'bg-green-100 text-green-800'
        }
    ]
    
    return render(request, 'matchfinder/index.html', {'events': dummy_events})
