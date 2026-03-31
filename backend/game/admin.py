from django.contrib import admin
from .models import Location, GameState


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('sequence_in_journey', 'name', 'latitude', 'longitude')
    ordering = ('sequence_in_journey',)
    search_fields = ('name',)


@admin.register(GameState)
class GameStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_location',
                    'days_remaining', 'cash', 'bugs', 'morale')
    list_filter = ('days_remaining', 'bugs')
