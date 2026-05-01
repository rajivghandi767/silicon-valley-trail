# Place this in views.py (or import it from a new file)
import json
from ..models import Location


class CacheGameState:
    def __init__(self, current_location_id, cash=2500, award_miles=8000, morale=100, bugs=0, days_remaining=18):
        self.current_location_id = current_location_id
        self.cash = cash
        self.award_miles = award_miles
        self.morale = morale
        self.bugs = bugs
        self.days_remaining = days_remaining

    @property
    def is_lost(self):
        return self.morale <= 0 or self.bugs >= 50 or self.days_remaining <= 0 or self.cash < 0

    @property
    def is_won(self):
        return self.current_location_id == 10

    def serialize_for_api(self):

        # Fetch the persistent Location object using the cached ID
        location = Location.objects.filter(
            sequence_in_journey=self.current_location_id).first()

        if self.is_won:
            status_text = "MISSION ACCOMPLISHED. Secure connection closed."
        elif self.is_lost:
            status_text = "SYSTEM FAILURE. Secure connection closed."
        else:
            status_text = f"Currently in {location.name} with ${self.cash} cash, {self.award_miles} miles, {self.morale}% morale, {self.bugs} bugs, and {self.days_remaining} days remaining."

        return {
            "current_location": location.name if location else "Unknown",
            "description": location.description if location else "",
            "sequence_in_journey": location.sequence_in_journey if location else 1,
            "cash": self.cash,
            "award_miles": self.award_miles,
            "morale": self.morale,
            "bugs": self.bugs,
            "days_remaining": self.days_remaining,
            "is_lost": self.is_lost,
            "is_won": self.is_won,
            "status_summary": status_text,
        }
