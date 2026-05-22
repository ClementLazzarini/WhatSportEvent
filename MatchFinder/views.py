from django.http import HttpResponse
from django.shortcuts import render

def simple_view(request):
    response = HttpResponse('<html><body>Hello World</body></html>')
    return render(request, 'MatchFinder/index.html')

