from django.urls import path
from . import models, views

urlpatterns = [
    path('', views.simple_view),
]
