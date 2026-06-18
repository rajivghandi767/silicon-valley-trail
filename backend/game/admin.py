from django.contrib import admin
from .models import Location, ReportedIssue


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("sequence_in_journey", "name", "latitude", "longitude")
    ordering = ("sequence_in_journey",)
    search_fields = ("name",)


@admin.register(ReportedIssue)
class ReportedIssueAdmin(admin.ModelAdmin):
    list_display = ("issue_type", "created_at", "resolved")
    list_filter = ("resolved", "issue_type")
    search_fields = ("user_note",)
    readonly_fields = ("created_at",)
