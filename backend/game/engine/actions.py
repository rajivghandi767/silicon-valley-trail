# backend/game/engine/actions.py
from ..models import Location
from ..services.weather import check_marine_conditions, check_aviation_conditions
from .events import trigger_random_event
from .constants import (
    ACTION_BASE_MESSAGES,
    TRAVEL_MESSAGES,
    STATIONARY_ACTION_IMPACTS,
    TRAVEL_IMPACTS
)


def apply_impacts(game, impacts):
    """
    Helper function to dynamically apply a dictionary of stat changes to the game state.
    """
    for stat, change_value in impacts.items():
        if hasattr(game, stat):
            current_value = getattr(game, stat)
            setattr(game, stat, current_value + change_value)


def process_turn(game, action):
    """
    Processes the player's action, applies weather conditions, destination rewards via ORM,
    and random events, returning a tuple of (turn_message, error_string).
    """
    turn_message = "> Action initiated...\n\n"
    successful_travel = False
    error = None

    # 1. STATIONARY ACTIONS
    if action in STATIONARY_ACTION_IMPACTS:
        apply_impacts(game, STATIONARY_ACTION_IMPACTS[action])
        turn_message += ACTION_BASE_MESSAGES.get(action, "")
        return turn_message, error

    # 2. TRAVEL ACTIONS
    elif action in ['travel_ferry', 'travel_flight']:
        next_loc = Location.objects.filter(
            sequence_in_journey=game.current_location_id + 1).first()

        if not next_loc:
            return turn_message, TRAVEL_MESSAGES['error_no_location']

        if action == 'travel_ferry':
            is_rough_seas, wave_height = check_marine_conditions(
                next_loc.latitude, next_loc.longitude)
            turn_message += TRAVEL_MESSAGES['ferry_sea_conditions'].format(
                wave_height=wave_height)

            if is_rough_seas:
                apply_impacts(game, TRAVEL_IMPACTS['ferry_grounded'])
                turn_message += TRAVEL_MESSAGES['ferry_grounded']
            else:
                apply_impacts(game, TRAVEL_IMPACTS['ferry_success'])
                game.current_location_id = next_loc.sequence_in_journey
                successful_travel = True
                turn_message += TRAVEL_MESSAGES['ferry_success'].format(
                    location_name=next_loc.name)

        elif action == 'travel_flight':
            # Check if the player has enough miles before flying
            if game.award_miles < TRAVEL_IMPACTS['flight_cost_threshold']:
                return turn_message, TRAVEL_MESSAGES['flight_insufficient_miles']

            is_thunderstorm, is_turbulent = check_aviation_conditions(
                next_loc.latitude, next_loc.longitude)

            if is_thunderstorm:
                apply_impacts(game, TRAVEL_IMPACTS['flight_grounded'])
                turn_message += TRAVEL_MESSAGES['flight_grounded']
            else:
                apply_impacts(game, TRAVEL_IMPACTS['flight_cost'])
                game.current_location_id = next_loc.sequence_in_journey
                successful_travel = True

                if is_turbulent:
                    apply_impacts(game, TRAVEL_IMPACTS['flight_turbulent'])
                    turn_message += TRAVEL_MESSAGES['flight_turbulent'].format(
                        location_name=next_loc.name)
                else:
                    apply_impacts(game, TRAVEL_IMPACTS['flight_smooth'])
                    turn_message += TRAVEL_MESSAGES['flight_smooth'].format(
                        location_name=next_loc.name)

        # 3. APPLY POST-TRAVEL EVENTS
        if successful_travel and next_loc:

            # A. Guaranteed Destination Reward (via Django ORM)
            if next_loc.reward_stat and hasattr(game, next_loc.reward_stat):
                current_stat = getattr(game, next_loc.reward_stat)
                setattr(game, next_loc.reward_stat,
                        current_stat + next_loc.reward_amount)

                if next_loc.reward_message:
                    turn_message += f"\n\n> Destination Arrival: {next_loc.reward_message}"

            # B. Dynamic Random Event
            event_message = trigger_random_event(game, next_loc.name)
            turn_message += f"\n\n> {event_message}"

    else:
        error = TRAVEL_MESSAGES['error_invalid_action']

    return turn_message, error
