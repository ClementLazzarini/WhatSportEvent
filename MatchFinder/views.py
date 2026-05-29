from django.shortcuts import render
from .models import Event

def home_view(request):
    search_city = request.GET.get('city', '')
    events = Event.objects.select_related('sport').order_by('start_time')

    if search_city:
        events = events.filter(city__icontains=search_city)

    events = events[:12]
    context = {
        'events': events,
        'search_city': search_city
    }

    # --- MAGIE HTMX ICI ---
    # Si la requête vient de HTMX, on ne renvoie QUE la grille des matchs
    if request.headers.get('HX-Request'):
        return render(request, 'matchfinder/partials/event_list.html', context)
    
    # Sinon (premier chargement de la page), on renvoie la page entière
    return render(request, 'matchfinder/index.html', context)