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
        """
        Refactored loss conditions to account for when winning is no longer mathematically possible, even if the player hasn't technically run out of resources yet. This prevents scenarios where a player could continue playing indefinitely in a hopeless situation, and provides clearer feedback on why they lost.
        """
        stops_remaining = 10 - self.current_location.sequence_in_journey
        if self.days_remaining < stops_remaining:
            return True
        if self.morale <= 0:
            return True
        if self.bugs >= 50:
            return True
        if self.cash < 0 and self.award_miles < 0:
            return True
        return False
        # Loss conditions: Running out of cash, miles, morale, or reaching the bug threshold or day limit.
        # return self.morale <= 0 or self.bugs >= 50 or self.days_remaining <= 0 or self.cash < 0

    @property
    def is_won(self):
        """
        Refactored to Explicitly check for the win condition of reaching the final destination (Stop 10) while ensuring the player hasn't already lost. This prevents any edge cases where a player might technically reach Stop 10 but has already triggered a loss condition, ensuring the game logic remains consistent and intuitive.
        """
        # Win condition: Successfully reaching the final destination (Stop 10). Resource checks are handled by the is_lost property above.
        return self.current_location.sequence_in_journey == 10 and not self.is_lost

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
