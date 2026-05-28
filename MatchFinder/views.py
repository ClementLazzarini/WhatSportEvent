from django.shortcuts import render
from .models import Event

def home_view(request):
    events = Event.objects.select_related('sport').order_by('start_time')[:12]
    
    return render(request, 'matchfinder/index.html', {'events': events})