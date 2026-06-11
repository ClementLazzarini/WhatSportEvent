import json
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
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

def map_view(request):
    now = timezone.now()
    
    # 1. On récupère les événements futurs avec coordonnées
    events = Event.objects.filter(
        latitude__isnull=False, 
        longitude__isnull=False,
        start_time__gte=now
    ).select_related('sport').order_by('start_time')
    
    # 2. Récupération des filtres
    search_sport = request.GET.get('sport', '')
    search_date = request.GET.get('date', 'all')
    
    # 3. Filtrage par sport
    if search_sport:
        events = events.filter(sport__slug=search_sport)
        
    # 4. Filtrage temporel
    if search_date == 'week':
        events = events.filter(start_time__gte=now, start_time__lte=now + timedelta(days=7))
    elif search_date == 'month':
        events = events.filter(start_time__gte=now, start_time__lte=now + timedelta(days=30))
    
    # 5. Création du JSON pour JavaScript
    events_data = []
    for event in events:
        events_data.append({
            'title': event.title,
            'sport': event.sport.name,
            'lat': event.latitude,
            'lon': event.longitude,
            'venue': event.venue_name,
            'city': event.city,
            'date': event.start_time.strftime("%d %b, %H:%M"),
            'url': reverse('event_detail', args=[event.id])
        })
        
    context = {
        'events_json': json.dumps(events_data, cls=DjangoJSONEncoder),
        'sports': Sport.objects.all(),
        'search_sport': search_sport,
        'search_date': search_date
    }

    # 6. Magie HTMX
    if request.headers.get('HX-Request'):
        return render(request, 'matchfinder/partials/map_data.html', context)
        
    return render(request, 'matchfinder/map.html', context)
