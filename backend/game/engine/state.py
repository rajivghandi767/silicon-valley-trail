# backend/game/engine/state.py
from django.core.cache import cache
from ..models import Location
from .constants import STATUS_WON, STATUS_LOST, STATUS_ACTIVE, DEFEAT_MESSAGES


class CacheGameState:
    def __init__(
        self,
        current_location_id,
        cash=2500,
        award_miles=8000,
        morale=100,
        bugs=0,
        days_remaining=18,
    ):
        self.current_location_id = current_location_id
        self.cash = cash
        self.award_miles = award_miles
        self.morale = morale
        self.bugs = bugs
        self.days_remaining = days_remaining

    @property
    def total_stops(self):
        """
        Dynamically fetches the total number of map locations from the database.

        Because the total number of stops dictates win/loss boundary conditions, we cache this
        value indefinitely using Redis. This eliminates a recurrent `SELECT COUNT(*)`
        query from executing on every single player action.
        """
        return cache.get_or_set("svt_total_stops", Location.objects.count, timeout=None)

    @property
    def is_lost(self):
        stops_remaining = 10 - self.current_location_id
        if self.days_remaining < stops_remaining:
            return True
        if self.morale <= 0:
            return True
        if self.bugs >= 50:
            return True
        if self.cash < 0 and self.award_miles < 0:
            return True
        return False

    @property
    def is_won(self):
        return self.current_location_id == 10 and not self.is_lost

    def apply_boundaries(self):
        """Prevents negative states from hitting the UI"""
        self.morale = max(0, min(100, self.morale))
        self.bugs = max(0, self.bugs)

    def get_loss_reason(self):
        """Maps the exact loss condition to the constant message"""
        stops_remaining = 10 - self.current_location_id
        if self.days_remaining < stops_remaining:
            return DEFEAT_MESSAGES["time"]
        if self.cash < 0 and self.award_miles < 0:
            return DEFEAT_MESSAGES["bankrupt"]
        if self.bugs >= 50:
            return DEFEAT_MESSAGES["bugs"]
        if self.morale <= 0:
            return DEFEAT_MESSAGES["morale"]
        return "SYSTEM FAILURE."

    def serialize_for_api(self):
        """
        Prepares the current game state to be returned to the React frontend.

        Fetches the current Location object for descriptions/names. To prevent a database
        lookup on every user interaction (e.g., resting, coding, traveling), we heavily cache
        the individual Location objects indefinitely.
        """

        def fetch_loc():
            return Location.objects.filter(
                sequence_in_journey=self.current_location_id
            ).first()

        location = cache.get_or_set(
            f"svt_location_{self.current_location_id}", fetch_loc, timeout=None
        )

        format_kwargs = {
            "location_name": location.name if location else "Unknown",
            "cash": self.cash,
            "award_miles": self.award_miles,
            "morale": self.morale,
            "bugs": self.bugs,
            "days_remaining": self.days_remaining,
        }

        if self.is_won:
            status_text = STATUS_WON.format(**format_kwargs)
        elif self.is_lost:
            status_text = STATUS_LOST.format(**format_kwargs)
        else:
            status_text = STATUS_ACTIVE.format(**format_kwargs)

        return {
            "current_location": location.name if location else "Unknown",
            "description": location.description if location else "",
            "sequence_in_journey": location.sequence_in_journey if location else 1,
            "total_stops": self.total_stops,
            "cash": self.cash,
            "award_miles": self.award_miles,
            "morale": self.morale,
            "bugs": self.bugs,
            "days_remaining": self.days_remaining,
            "is_lost": self.is_lost,
            "is_won": self.is_won,
            "status_summary": status_text,
        }
