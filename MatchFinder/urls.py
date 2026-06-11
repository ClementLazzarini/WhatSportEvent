from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('event/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('carte/', views.map_view, name='map'),
]