import json
from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import ReportedIssue
from .engine.constants import INTRO_MESSAGE, REBOOT_MESSAGE, VICTORY_MESSAGE, SESSION_RESTORED_MESSAGE
from .engine.state import CacheGameState
from .engine.actions import process_turn


def get_session_cache_key(request: HttpRequest) -> str:
    """Retrieves or provisions a tracking key tied to the Django session."""
    if not request.session.session_key:
        request.session.create()
        request.session['initialized'] = True
    return f"svt_game_{request.session.session_key}"


@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_state(request: HttpRequest) -> JsonResponse:
    cache_key = get_session_cache_key(request)
    game = cache.get(cache_key)

    # Auto-initialize a new game if one isn't found instead of throwing a 404
    if not game:
        game = CacheGameState(current_location_id=1)
        cache.set(cache_key, game, timeout=86400)

        response_data = game.serialize_for_api()
        response_data["message"] = INTRO_MESSAGE
        return JsonResponse(response_data)

    response_data = game.serialize_for_api()

    if game.is_won:
        display_message = VICTORY_MESSAGE.format(
            days=game.days_remaining, cash=game.cash, miles=game.award_miles, morale=game.morale, bugs=game.bugs
        )
    else:
        location_name = response_data.get('current_location', 'UNKNOWN')
        display_message = SESSION_RESTORED_MESSAGE.format(
            location_name=location_name, stop_number=game.current_location_id)

    response_data["message"] = display_message
    return JsonResponse(response_data)


@require_http_methods(["POST"])
def take_action(request: HttpRequest) -> JsonResponse:
    cache_key = get_session_cache_key(request)
    game = cache.get(cache_key)

    if not game:
        return JsonResponse({"error": "Your session has expired. Please refresh the page to start a new game."}, status=404)

    if game.is_lost or game.is_won:
        return JsonResponse({"error": "The game has ended. Please restart."}, status=400)

    try:
        data = json.loads(request.body)
        raw_action = data.get("action", "")

        # Delegate game logic to the engine
        turn_message, error = process_turn(game, raw_action)

        if error:
            return JsonResponse({"error": error}, status=400)

        # Apply bounds and save to Redis
        game.apply_boundaries()
        cache.set(cache_key, game, timeout=86400)

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
def restart_game(request: HttpRequest) -> JsonResponse:
    cache_key = get_session_cache_key(request)

    new_game = CacheGameState(current_location_id=1)
    cache.set(cache_key, new_game, timeout=86400)

    response_data = new_game.serialize_for_api()
    response_data["message"] = REBOOT_MESSAGE
    return JsonResponse(response_data, status=200)


@require_http_methods(["POST"])
def submit_report(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        ReportedIssue.objects.create(
            issue_type=data.get("issue_type", "other"),
            user_note=data.get("user_note", "")
        )
        return JsonResponse({"status": "success", "message": "Report saved."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
