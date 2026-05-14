from typing import Tuple, Optional, Dict, Any

from ..models import Location
from ..services.weather import check_marine_conditions, check_aviation_conditions
from .events import trigger_random_event
from .constants import (
    GameAction,
    STATIONARY_ACTIONS,
    TRAVEL_ACTIONS,
    STATIONARY_ACTION_IMPACTS,
    TRAVEL_IMPACTS,
    ACTION_BASE_MESSAGES,
    TRAVEL_MESSAGES
)


def apply_impacts(game: Any, impacts: Dict[str, int]) -> None:
    """
    Helper function to dynamically apply a dictionary of stat/resource changes.
    """
    for stat, change_value in impacts.items():
        if hasattr(game, stat):
            current_value = getattr(game, stat)
            setattr(game, stat, current_value + change_value)


def process_turn(game: Any, raw_action: str) -> Tuple[str, Optional[str]]:
    """
    Processes the player's action, applies weather conditions, destination rewards,
    and random events.
    """
    turn_message: str = "> Action initiated...\n\n"
    successful_travel: bool = False
    error: Optional[str] = None
    next_location: Optional[Location] = None

    # 1. API BOUNDARY VALIDATION
    try:
        action = GameAction(raw_action)
    except ValueError:
        valid_actions_str = ", ".join([a.value for a in GameAction])
        error = f"Invalid/unknown action. Please select from: {valid_actions_str}."
        return turn_message, error

    # 2. ACTION ROUTING (Structural Pattern Matching)
    match action:

        # STATIONARY ACTIONS
        case a if a in STATIONARY_ACTIONS:
            apply_impacts(game, STATIONARY_ACTION_IMPACTS[a])
            turn_message += ACTION_BASE_MESSAGES.get(a, "")

        # TRAVEL ACTIONS
        case a if a in TRAVEL_ACTIONS:
            next_location = Location.objects.filter(
                sequence_in_journey=game.current_location_id + 1).first()

            if not next_location:
                return turn_message, TRAVEL_MESSAGES['error_no_location']

            if a == GameAction.FERRY:
                is_rough_seas, wave_height = check_marine_conditions(
                    next_location.latitude, next_location.longitude)
                turn_message += TRAVEL_MESSAGES['ferry_sea_conditions'].format(
                    wave_height=wave_height)

                if is_rough_seas:
                    apply_impacts(game, TRAVEL_IMPACTS['ferry_grounded'])
                    turn_message += TRAVEL_MESSAGES['ferry_grounded']
                else:
                    apply_impacts(game, TRAVEL_IMPACTS['ferry_success'])
                    game.current_location_id = next_location.sequence_in_journey
                    successful_travel = True
                    turn_message += TRAVEL_MESSAGES['ferry_success'].format(
                        location_name=next_location.name)

            elif a == GameAction.FLIGHT:
                if game.award_miles < TRAVEL_IMPACTS['flight_cost_threshold']:
                    return turn_message, TRAVEL_MESSAGES['flight_insufficient_miles']

                is_thunderstorm, is_turbulent = check_aviation_conditions(
                    next_location.latitude, next_location.longitude)

                if is_thunderstorm:
                    apply_impacts(game, TRAVEL_IMPACTS['flight_grounded'])
                    turn_message += TRAVEL_MESSAGES['flight_grounded']
                else:
                    apply_impacts(game, TRAVEL_IMPACTS['flight_cost'])
                    game.current_location_id = next_location.sequence_in_journey
                    successful_travel = True

                    if is_turbulent:
                        apply_impacts(game, TRAVEL_IMPACTS['flight_turbulent'])
                        turn_message += TRAVEL_MESSAGES['flight_turbulent'].format(
                            location_name=next_location.name)
                    else:
                        apply_impacts(game, TRAVEL_IMPACTS['flight_smooth'])
                        turn_message += TRAVEL_MESSAGES['flight_smooth'].format(
                            location_name=next_location.name)

    # 3. APPLY POST-TRAVEL EVENTS
    if successful_travel and next_location:
        if next_location.reward_resource and hasattr(game, next_location.reward_resource):
            current_resource = getattr(game, next_location.reward_resource)
            setattr(game, next_location.reward_resource,
                    current_resource + next_location.reward_amount)

            if next_location.reward_message:
                turn_message += f"\n\n> Destination Arrival: {next_location.reward_message}"

        event_message = trigger_random_event(game, next_location.name)
        turn_message += f"\n\n> {event_message}"

    return turn_message, error
