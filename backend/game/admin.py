from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('sequence_in_journey', 'name', 'latitude', 'longitude')
    ordering = ('sequence_in_journey',)
    search_fields = ('name',)
