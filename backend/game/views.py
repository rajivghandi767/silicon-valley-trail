import json
from django.core.cache import cache
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import ReportedIssue
from .engine.constants import (
    INTRO_MESSAGE,
    REBOOT_MESSAGE,
    VICTORY_MESSAGE,
    SESSION_RESTORED_MESSAGE,
    GAME_SESSION_TTL,
    STARTING_LOCATION_ID,
    MAX_REPORT_NOTE_LENGTH,
    REPORT_RATE_LIMIT_MAX,
    REPORT_RATE_LIMIT_WINDOW,
)
from .engine.state import CacheGameState
from .engine.actions import process_turn


def get_session_cache_key(request: HttpRequest) -> str:
    """
    Retrieves or provisions a tracking key tied to the Django session.
    
    This function uses Django's session framework to generate a unique identifier 
    for the current user. If no session exists, it initializes one. 
    This allows us to maintain the player's game state across requests (and page reloads)
    without needing a formal authentication system (like a login page).
    
    Args:
        request: The incoming HTTP request.
    
    Returns:
        A formatted string used as the key to store/retrieve the game state in Redis.
    """
    if not request.session.session_key:
        request.session.create()
        request.session["initialized"] = True
    return f"svt_game_{request.session.session_key}"


@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_state(request: HttpRequest) -> JsonResponse:
    """
    Retrieves the current game state for the player.
    
    The @ensure_csrf_cookie decorator guarantees that a CSRF token is sent to the 
    frontend, which is necessary since we use a decoupled React SPA. Subsequent POST
    requests will include this token to verify their authenticity.
    """
    cache_key = get_session_cache_key(request)
    game = cache.get(cache_key)

    # Auto-initialize a new game if one isn't found instead of throwing a 404.
    # This ensures a seamless onboarding experience for first-time visitors.
    if not game:
        game = CacheGameState(current_location_id=STARTING_LOCATION_ID)
        cache.set(cache_key, game, timeout=GAME_SESSION_TTL)

        response_data = game.serialize_for_api()
        response_data["message"] = INTRO_MESSAGE.format(days_remaining=game.days_remaining)
        return JsonResponse(response_data)

    response_data = game.serialize_for_api()

    # Determine the contextually appropriate status message based on whether the game is over
    if game.is_won:
        location_name = response_data.get("current_location", "UNKNOWN")
        display_message = VICTORY_MESSAGE.format(
            location_name=location_name,
            days_remaining=game.days_remaining,
            cash=game.cash,
            miles=game.award_miles,
            morale=game.morale,
            bugs=game.bugs,
        )
    else:
        location_name = response_data.get("current_location", "UNKNOWN")
        display_message = SESSION_RESTORED_MESSAGE.format(
            location_name=location_name, stop_number=game.current_location_id
        )

    response_data["message"] = display_message
    return JsonResponse(response_data)


@require_http_methods(["POST"])
def take_action(request: HttpRequest) -> JsonResponse:
    """
    Processes a player's action (e.g., code, travel, rest) and updates the game state.
    
    This view demonstrates a typical decoupled architectural pattern:
    1. Validation: Ensures the session exists and the game hasn't ended.
    2. Delegation: Passes the core business logic (turn processing) to a separate engine module.
    3. Persistence: Updates the in-memory cache with the new state bounds applied.
    4. Presentation: Serializes the updated domain models back into JSON for the frontend client.
    """
    cache_key = get_session_cache_key(request)
    game = cache.get(cache_key)

    if not game:
        return JsonResponse(
            {
                "error": "Your session has expired. Please refresh the page to start a new game."
            },
            status=404,
        )

    if game.is_lost or game.is_won:
        return JsonResponse(
            {"error": "The game has ended. Please restart."}, status=400
        )

    try:
        data = json.loads(request.body)
        raw_action = data.get("action", "")

        # Delegate game logic to the engine module.
        # This keeps our views thin and focused strictly on HTTP concerns,
        # moving complex rules processing into testable service layers.
        turn_message, error = process_turn(game, raw_action)

        if error:
            return JsonResponse({"error": error}, status=400)

        # Ensure metrics stay within valid ranges (e.g., max morale is 100) before persisting
        game.apply_boundaries()
        cache.set(cache_key, game, timeout=GAME_SESSION_TTL)

        if game.is_won:
            temp_response = game.serialize_for_api()
            turn_message = VICTORY_MESSAGE.format(
                location_name=temp_response.get("current_location", "UNKNOWN"),
                days_remaining=game.days_remaining,
                cash=game.cash,
                miles=game.award_miles,
                morale=game.morale,
                bugs=game.bugs,
            )
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

    new_game = CacheGameState(current_location_id=STARTING_LOCATION_ID)
    cache.set(cache_key, new_game, timeout=GAME_SESSION_TTL)

    response_data = new_game.serialize_for_api()
    response_data["message"] = REBOOT_MESSAGE.format(days_remaining=new_game.days_remaining)
    return JsonResponse(response_data, status=200)


@require_http_methods(["POST"])
def submit_report(request: HttpRequest) -> JsonResponse:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    client_ip = (
        x_forwarded_for.split(",")[0].strip()
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR", "unknown")
    )
    rate_key = f"svt_report_rate_{client_ip}"
    current_count = cache.get(rate_key, 0)
    if isinstance(current_count, int) and current_count >= REPORT_RATE_LIMIT_MAX:
        return JsonResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status=429,
        )

    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        raw_issue_type = data.get("issue_type", ReportedIssue.IssueTypeChoices.OTHER)
        if (
            not isinstance(raw_issue_type, str)
            or raw_issue_type not in ReportedIssue.IssueTypeChoices.values
        ):
            return JsonResponse({"error": "Invalid issue type."}, status=400)

        raw_note = data.get("user_note", "")
        if not isinstance(raw_note, str):
            return JsonResponse({"error": "Invalid note format."}, status=400)

        user_note = raw_note.strip()
        if not user_note:
            return JsonResponse({"error": "Report note cannot be empty."}, status=400)
        if len(user_note) > MAX_REPORT_NOTE_LENGTH:
            return JsonResponse(
                {
                    "error": f"Report note cannot exceed {MAX_REPORT_NOTE_LENGTH} characters."
                },
                status=400,
            )

        issue = ReportedIssue.objects.create(
            issue_type=raw_issue_type, user_note=user_note
        )
        cache.set(
            rate_key,
            (current_count if isinstance(current_count, int) else 0) + 1,
            timeout=REPORT_RATE_LIMIT_WINDOW,
        )
        issue.send_notifications()

        return JsonResponse({"status": "success", "message": "Report saved."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
