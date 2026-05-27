from django.db import models
from django.utils import timezone

class Sport(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom du sport")
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="Classe CSS pour l'icône (ex: fa-futbol)")

    class Meta:
        verbose_name = "Sport"
        verbose_name_plural = "Sports"
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre de l'événement")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='events')
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Dates et heures
    start_time = models.DateTimeField(verbose_name="Début")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Fin (optionnel)")
    
    # Localisation
    venue_name = models.CharField(max_length=150, verbose_name="Nom du lieu (ex: Stade Ernest-Wallon)")
    city = models.CharField(max_length=100, default="Toulouse", verbose_name="Ville")
    
    # Infos pratiques
    price = models.CharField(max_length=50, blank=True, verbose_name="Prix", help_text="Ex: Gratuit, 10€, Prix libre")
    ticket_link = models.URLField(blank=True, verbose_name="Lien billetterie / Infos")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    external_api_id = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True, 
        help_text="ID unique de l'événement provenant de l'API"
    )

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%d/%m/%Y')}"