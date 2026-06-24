# backend/game/engine/state.py
from typing import Optional, Dict, Any
from django.core.cache import cache
from ..models import Location
from .constants import STATUS_WON, STATUS_LOST, STATUS_ACTIVE, DEFEAT_MESSAGES, WARNING_THRESHOLDS, STARTING_FIXED_STATS, DYNAMIC_RESOURCE_MULTIPLIERS, CRITICAL_THRESHOLDS, BOUNDARY_LIMITS, STARTING_LOCATION_ID


class CacheGameState:
    def __init__(
        self,
        current_location_id: int,
        cash: Optional[int] = None,
        award_miles: Optional[int] = None,
        morale: Optional[int] = None,
        bugs: Optional[int] = None,
        days_remaining: Optional[int] = None,
    ) -> None:
        self.current_location_id = current_location_id

        # Calculate journey length dynamically to scale difficulty
        jumps = self.total_stops - STARTING_LOCATION_ID

        # Dynamically scan the database for any intrinsic cash rewards the player will earn
        # We deduct this from the starting cash to guarantee the mathematical squeeze is never broken!
        def fetch_cash_rewards() -> int:
            return sum(
                loc.reward_amount
                for loc in Location.objects.filter(reward_resource="cash", sequence_in_journey__lt=self.total_stops)
            )

        total_cash_rewards = cache.get_or_set(
            "svt_cash_rewards", fetch_cash_rewards, timeout=None)
        assert isinstance(total_cash_rewards, int)

        # Dynamic Resource Assignment
        base_cash = int(
            (jumps * DYNAMIC_RESOURCE_MULTIPLIERS["cash_per_jump"]) + DYNAMIC_RESOURCE_MULTIPLIERS["cash_buffer_flat"])
        self.cash = cash if cash is not None else max(
            0, base_cash - total_cash_rewards)

        self.days_remaining = days_remaining if days_remaining is not None else int(
            (jumps * DYNAMIC_RESOURCE_MULTIPLIERS["days_per_jump"]) + DYNAMIC_RESOURCE_MULTIPLIERS["days_buffer_flat"])

        num_flights = int(
            jumps / DYNAMIC_RESOURCE_MULTIPLIERS["jumps_per_flight"])
        self.award_miles = award_miles if award_miles is not None else int(num_flights *
                                                                           DYNAMIC_RESOURCE_MULTIPLIERS["flight_cost_miles"])

        # Fixed Resource Assignment
        self.morale = morale if morale is not None else STARTING_FIXED_STATS["morale"]
        self.bugs = bugs if bugs is not None else STARTING_FIXED_STATS["bugs"]

    @property
    def total_stops(self) -> int:
        """
        Dynamically fetches the total number of map locations from the database.

        Because the total number of stops dictates win/loss boundary conditions, we cache this
        value indefinitely using Redis. This eliminates a recurrent `SELECT COUNT(*)`
        query from executing on every single player action, significantly reducing database load.
        """
        total_stops = cache.get_or_set(
            "svt_total_stops", lambda: Location.objects.count(), timeout=None)
        assert isinstance(total_stops, int)
        return total_stops

    @property
    def is_lost(self) -> bool:
        # If the player has reached the final destination, Victory trumps all loss conditions
        if self.current_location_id == self.total_stops:
            return False

        stops_remaining = self.total_stops - self.current_location_id
        if self.days_remaining < stops_remaining:
            return True
        if self.morale <= CRITICAL_THRESHOLDS["MORALE"]:
            return True
        if self.bugs >= CRITICAL_THRESHOLDS["BUGS"]:
            return True
        from .constants import TRAVEL_IMPACTS
        if self.cash <= CRITICAL_THRESHOLDS["CASH"] and self.award_miles < TRAVEL_IMPACTS["flight_cost_threshold"]:
            return True
        return False

    @property
    def is_won(self) -> bool:
        return self.current_location_id == self.total_stops

    def apply_boundaries(self) -> None:
        """
        Prevents negative states from hitting the UI.

        This acts as a normalization step before persisting the state back to the cache. 
        It ensures the frontend never receives invalid numbers (e.g. -10 bugs or 105% morale).
        """
        self.morale = max(BOUNDARY_LIMITS["MORALE_MIN"], min(
            BOUNDARY_LIMITS["MORALE_MAX"], self.morale))
        self.bugs = max(BOUNDARY_LIMITS["BUGS_MIN"], self.bugs)
        self.cash = max(BOUNDARY_LIMITS["CASH_MIN"], self.cash)
        self.award_miles = max(BOUNDARY_LIMITS["MILES_MIN"], self.award_miles)

    def get_loss_reason(self) -> str:
        """Maps the exact loss condition to the constant message"""
        stops_remaining = self.total_stops - self.current_location_id
        if self.days_remaining < stops_remaining:
            return DEFEAT_MESSAGES["time"]
        from .constants import TRAVEL_IMPACTS
        if self.cash <= CRITICAL_THRESHOLDS["CASH"] and self.award_miles < TRAVEL_IMPACTS["flight_cost_threshold"]:
            return DEFEAT_MESSAGES["bankrupt"]
        if self.bugs >= CRITICAL_THRESHOLDS["BUGS"]:
            return DEFEAT_MESSAGES["bugs"]
        if self.morale <= CRITICAL_THRESHOLDS["MORALE"]:
            return DEFEAT_MESSAGES["morale"]
        return "SYSTEM FAILURE."

    def serialize_for_api(self) -> Dict[str, Any]:
        """
        Prepares the current game state to be returned to the React frontend.

        Fetches the current Location object for descriptions/names. To prevent a database
        lookup on every user interaction (e.g., resting, coding, traveling), we heavily cache
        the individual Location objects indefinitely. The `fetch_loc` closure is only executed 
        if the cache misses.
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

        stat_statuses = {
            "days": "critical" if self.days_remaining <= WARNING_THRESHOLDS["DAYS"] else "good",
            "cash": "critical" if self.cash <= WARNING_THRESHOLDS["CASH"] else "good",
            "miles": "default" if self.award_miles < WARNING_THRESHOLDS["MILES"] else "blue",
            "morale": "critical" if self.morale <= WARNING_THRESHOLDS["MORALE"] else "good",
            "bugs": "critical" if self.bugs >= WARNING_THRESHOLDS["BUGS_CRITICAL"]
                    else "warning" if self.bugs >= WARNING_THRESHOLDS["BUGS_WARNING"]
                    else "good",
        }

        return {
            "current_location": location.name if location else "Unknown",
            "description": location.description if location else "",
            "sequence_in_journey": location.sequence_in_journey if location else STARTING_LOCATION_ID,
            "total_stops": self.total_stops,
            "cash": self.cash,
            "award_miles": self.award_miles,
            "morale": self.morale,
            "bugs": self.bugs,
            "days_remaining": self.days_remaining,
            "is_lost": self.is_lost,
            "is_won": self.is_won,
            "status_summary": status_text,
            "stat_statuses": stat_statuses,
        }
