from django.shortcuts import render
from .models import Event, Sport

def home_view(request):
    # 1. On écoute la ville ET le sport dans l'URL
    search_city = request.GET.get('city', '')
    search_sport = request.GET.get('sport', '')

    # 2. Requêtes de base
    events = Event.objects.select_related('sport').order_by('start_time')
    sports = Sport.objects.all()

    # 3. Application des filtres cumulables
    if search_city:
        events = events.filter(city__icontains=search_city)
        
    if search_sport:
        events = events.filter(sport__slug=search_sport)

    events = events[:12]
    
    # 4. On passe tout au contexte
    context = {
        'events': events,
        'search_city': search_city,
        'search_sport': search_sport,
        'sports': sports,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'matchfinder/partials/event_list.html', context)
    
    return render(request, 'matchfinder/index.html', context)