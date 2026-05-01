import json
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Location
from .services.weather import check_marine_conditions, check_aviation_conditions
from .engine.constants import INTRO_MESSAGE, REBOOT_MESSAGE, VICTORY_MESSAGE, ACTION_BASE_MESSAGES
from .engine.state import CacheGameState
from .engine.events import trigger_random_event


def get_session_cache_key(request):
    if not request.session.session_key:
        request.session.create()
    return f"svt_game_{request.session.session_key}"


@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_state(request):
    cache_key = get_session_cache_key(request)
    game = cache.get(cache_key)

    if not game:
        return JsonResponse({"error": "No active game found. Start a new game."}, status=404)

    response_data = game.serialize_for_api()

    if game.is_won:
        display_message = VICTORY_MESSAGE.format(
            days=game.days_remaining, cash=game.cash, miles=game.award_miles, morale=game.morale, bugs=game.bugs
        )
    elif game.current_location_id == 1 and game.days_remaining == 18:
        display_message = INTRO_MESSAGE
    else:
        location_name = response_data.get('current_location', 'UNKNOWN')
        display_message = (
            "// SECURE SESSION RESTORED...\n"
            f"// RESUMING AT STOP {game.current_location_id}: {location_name.upper()}\n\n"
            "// Awaiting your next command..."
        )

    response_data["message"] = display_message
    return JsonResponse(response_data)


@require_http_methods(["POST"])
def take_action(request):
    cache_key = get_session_cache_key(request)
    game = cache.get(cache_key)

    if not game:
        return JsonResponse({"error": "No active game found."}, status=404)
    if game.is_lost or game.is_won:
        return JsonResponse({"error": "The game has ended. Please restart."}, status=400)

    try:
        data = json.loads(request.body)
        action = data.get("action")

        turn_message = f"> Action initiated...\n\n"
        successful_travel = False

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

        # 2. TRAVEL ACTIONS
        elif action in ['travel_ferry', 'travel_flight']:
            next_loc = Location.objects.filter(
                sequence_in_journey=game.current_location_id + 1).first()

            if action == 'travel_ferry':
                is_rough_seas, wave_height = check_marine_conditions(
                    next_loc.latitude, next_loc.longitude)
                turn_message += f"> Sea Conditions: {wave_height}m waves.\n\n"
                if is_rough_seas:
                    game.morale -= 20
                    game.days_remaining -= 1
                    turn_message += f"> Result: SMALL CRAFT ADVISORY! Ferries grounded. (-1 Day)"
                else:
                    game.cash -= 150
                    game.morale -= 10
                    game.days_remaining -= 1
                    game.current_location_id = next_loc.sequence_in_journey
                    successful_travel = True
                    turn_message += f"> Safely made it to {next_loc.name}. (-$150, -1 Day)"

            elif action == 'travel_flight':
                if game.award_miles < 2000:
                    return JsonResponse({"error": "Insufficient Award Miles."}, status=400)

                is_thunderstorm, is_turbulent = check_aviation_conditions(
                    next_loc.latitude, next_loc.longitude)
                if is_thunderstorm:
                    game.morale -= 15
                    game.days_remaining -= 1
                    turn_message += f"> Result: ATC GROUND STOP! Flights canceled. (-1 Day)"
                else:
                    game.award_miles -= 2000
                    game.days_remaining -= 1
                    game.current_location_id = next_loc.sequence_in_journey
                    successful_travel = True
                    if is_turbulent:
                        game.morale -= 15
                        turn_message += f"> Result: Landed in {next_loc.name}, awful flight. (-2000 Miles, -1 Day)"
                    else:
                        game.morale += 10
                        turn_message += f"> Result: Smooth flight to {next_loc.name}. (-2000 Miles, -1 Day)"

            # 3. RANDOM EVENTS
            if successful_travel and next_loc:
                event_message = trigger_random_event(
                    game, next_loc.name)  # See note below
                turn_message += f"\n\n> {event_message}"

        # 4. FINALIZE TURN
        game.apply_boundaries()
        cache.set(cache_key, game, timeout=86400)  # Save back to DB Cache

        if game.is_won:
            turn_message = VICTORY_MESSAGE.format(
                days=game.days_remaining, cash=game.cash, miles=game.award_miles, morale=game.morale, bugs=game.bugs)
        elif game.is_lost:
            turn_message = game.get_loss_reason()

        response_data = game.serialize_for_api()
        response_data["message"] = turn_message
        return JsonResponse(response_data, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def restart_game(request):
    cache_key = get_session_cache_key(request)

    # Initialize a fresh cache state starting at Location ID 1
    new_game = CacheGameState(current_location_id=1)
    cache.set(cache_key, new_game, timeout=86400)

    response_data = new_game.serialize_for_api()
    response_data["message"] = REBOOT_MESSAGE
    return JsonResponse(response_data, status=200)
