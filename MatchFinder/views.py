from django.shortcuts import render, get_object_or_404
from .models import Event, Sport

def home_view(request):
    # 1. On écoute la ville ET le sport dans l'URL
    search_city = request.GET.get('city', '')
    search_sport = request.GET.get('sport', '')
    search_league = request.GET.get('league', '')

    # 2. Requêtes de base
    events = Event.objects.select_related('sport').order_by('start_time')
    sports = Sport.objects.all()

    # 3. Application des filtres cumulables
    if search_city:
        events = events.filter(city__icontains=search_city)
        
    if search_sport:
        events = events.filter(sport__slug=search_sport)

    if search_league:
        events = events.filter(league_name=search_league)
    
    leagues = Event.objects.exclude(league_name='').values_list('league_name', flat=True).distinct().order_by('league_name')

    events = events[:12]
    
    # 4. On passe tout au contexte
    context = {
        'events': events,
        'search_city': search_city,
        'search_sport': search_sport,
        'search_league': search_league,
        'sports': sports,
        'leagues': leagues,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'matchfinder/partials/event_list.html', context)
    
    return render(request, 'matchfinder/index.html', context)


def event_detail_view(request, event_id):
    event = get_object_or_404(Event.objects.select_related('sport'), id=event_id)
    
    return render(request, 'matchfinder/event_detail.html', {'event': event})