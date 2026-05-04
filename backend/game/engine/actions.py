# backend/game/engine/actions.py
from ..models import Location
from ..services.weather import check_marine_conditions, check_aviation_conditions
from .events import trigger_random_event
from .constants import ACTION_BASE_MESSAGES, TRAVEL_MESSAGES


def process_turn(game, action):
    """
    Processes the player's action, applies weather conditions and random events,
    and returns a tuple of (turn_message, error_string).
    """
    turn_message = "> Action initiated...\n\n"
    successful_travel = False
    error = None

    # 1. STATIONARY ACTIONS
    if action in ACTION_BASE_MESSAGES:
        if action == 'rest':
            game.morale += 40
            game.cash -= 100
            game.days_remaining -= 1
        elif action == 'code':
            game.bugs -= 10
            game.morale -= 20
            game.days_remaining -= 1
        elif action == 'mentor':
            game.days_remaining -= 1
            game.morale += 20
            game.bugs -= 10
        turn_message += ACTION_BASE_MESSAGES[action]
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
                game.morale -= 20
                game.days_remaining -= 1
                turn_message += TRAVEL_MESSAGES['ferry_grounded']
            else:
                game.cash -= 150
                game.morale -= 10
                game.days_remaining -= 1
                game.current_location_id = next_loc.sequence_in_journey
                successful_travel = True
                turn_message += TRAVEL_MESSAGES['ferry_success'].format(
                    location_name=next_loc.name)

        elif action == 'travel_flight':
            if game.award_miles < 2000:
                return turn_message, TRAVEL_MESSAGES['flight_insufficient_miles']

            is_thunderstorm, is_turbulent = check_aviation_conditions(
                next_loc.latitude, next_loc.longitude)

            if is_thunderstorm:
                game.morale -= 15
                game.days_remaining -= 1
                turn_message += TRAVEL_MESSAGES['flight_grounded']
            else:
                game.award_miles -= 2000
                game.days_remaining -= 1
                game.current_location_id = next_loc.sequence_in_journey
                successful_travel = True

                if is_turbulent:
                    game.morale -= 15
                    turn_message += TRAVEL_MESSAGES['flight_turbulent'].format(
                        location_name=next_loc.name)
                else:
                    game.morale += 10
                    turn_message += TRAVEL_MESSAGES['flight_smooth'].format(
                        location_name=next_loc.name)

        # 3. RANDOM EVENTS
        if successful_travel and next_loc:
            event_message = trigger_random_event(game, next_loc.name)
            turn_message += f"\n\n> {event_message}"

    else:
        error = TRAVEL_MESSAGES['error_invalid_action']

    return turn_message, error
