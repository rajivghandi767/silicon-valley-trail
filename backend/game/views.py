import json
import random
import urllib.request
import urllib.error
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import GameState, Location


# ============================================================================
# EXTERNAL API INTEGRATION FUNCTIONS
# ============================================================================

# Using pure urllib to adhere strictly to the "minimum dependencies" objective. While 'requests' has better ergonomics, wrapping this in a timeout/try-except block guarantees that anyone can boot this locally without C-compiler/pip issues.

def check_marine_conditions(latitude, longitude):
    """
    Fetches real-time wave data from Open-Meteo's dedicated Marine API to assess sea conditions for travel via ferry.
    """
    # The dedicated Marine API endpoint requesting current wave_height in meters
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={latitude}&longitude={longitude}&current=wave_height"

    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'SiliconValleyTrail/1.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())

            # Extract the wave height (returns a float in meters)
            wave_height = data.get('current', {}).get('wave_height', 0.0)

            # 2.5 meters (approx 8.2 feet) is a standard threshold for ferry cancellations
            is_rough_seas = wave_height > 2.5

            return is_rough_seas, wave_height

    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Marine API Error: {e}")
        # Fail open: assume calm seas so the game doesn't break if the API goes down
        return False, 0.0


def check_aviation_conditions(latitude, longitude):
    """
    Fetches atmospheric weather to determine flight safety and turbulence.
    Uses WMO (World Meteorological Organization) weather codes.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"

    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'SiliconValleyTrail/1.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())

            weather_code = data.get(
                'current_weather', {}).get('weathercode', 0)
            wind_speed = data.get('current_weather', {}).get('windspeed', 0.0)

            # WMO Codes 95, 96, 99 indicate thunderstorms
            is_thunderstorm = weather_code >= 95

            # High winds cause turbulence but not necessarily cancellations for jets
            is_turbulent = wind_speed > 40.0

            return is_thunderstorm, is_turbulent

    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Aviation API Error: {e}")
        # Fail open: assume clear skies
        return False, False

# ==========================================
# ENDPOINT 1: Get the current game state
# ==========================================


@require_http_methods(["GET"])
def get_state(request):
    """
    API endpoint to retrieve the current game state. Fetches the current save file and sends it to React (frontend).
    """
    # Assuming a single game state for simplicity
    game_state = GameState.objects.first()
    if not game_state:
        return JsonResponse({"error": "No active game found. Start a new game."}, status=404)

    return JsonResponse(game_state.serialize_for_api())

# ==========================================
# ENDPOINT 2: The Core Game Loop
# ==========================================

# The React client only sends the intended 'action' (Dumb Client). This prevents users from opening Chrome DevTools and injecting {"cash": 99999} to fund their Caribbean vacation. We handle all resource math server-side.


@csrf_exempt
@require_http_methods(["POST"])
def take_action(request):
    """
    API endpoint to process a player's move. Expects a JSON payload with the action and any relevant parameters.
    """
    # ==========================================
    # 1. FETCH THE CURRENT GAME STATE
    # ==========================================

    game_state = GameState.objects.first()
    if not game_state:
        return JsonResponse({"error": "No active game found. Start a new game."}, status=404)
    if game_state.check_loss_condition() or game_state.check_win_condition():
        return JsonResponse({
            "error": "The game has already ended. Please restart.",
            "game_state": game_state.serialize_for_api()
        }, status=400)

    try:
        data = json.loads(request.body)
        action = data.get("action")
        turn_message = ""

        # ==========================================
        # 2. PROCESS THE PLAYER'S ACTION
        # ==========================================

        # --- TRAVEL ACTIONS ---
        if action in ['travel_ferry', 'travel_flight']:
            next_loc = Location.objects.filter(
                sequence_order=game_state.current_location.sequence_order + 1).first()
            if not next_loc:
                return JsonResponse({"error": "You are already at the final destination!"}, status=400)

            if action == 'travel_ferry':
                is_rough_seas, wave_height = check_marine_conditions(
                    next_loc.latitude, next_loc.longitude)
                if is_rough_seas:
                    game_state.morale -= 25
                    game_state.cash -= 100
                    game_state.days_remaining -= 1
                    game_state.save()
                    return JsonResponse({
                        "error": f"Small Craft Advisory! {wave_height}m waves at {next_loc.name} canceled the ferries. You lost a day and took a morale hit.",
                        "game_state": game_state.serialize_for_api()
                    }, status=400)

                game_state.cash -= 200
                game_state.morale -= 15
                game_state.days_remaining -= 1
                turn_message = f"You took the ferry to {next_loc.name}. The sea breeze was nice, but the trip was exhausting."

            elif action == 'travel_flight':
                if game_state.award_miles < 2000:
                    return JsonResponse({"error": "Not enough Award Miles to book a flight!"}, status=400)

                is_thunderstorm, is_turbulent = check_aviation_conditions(
                    next_loc.latitude, next_loc.longitude)
                if is_thunderstorm:
                    game_state.morale -= 10
                    game_state.days_remaining -= 1
                    game_state.save()
                    return JsonResponse({
                        "error": f"ATC Ground Stop! Thunderstorms at {next_loc.name} grounded all flights. You lost a day at the gate.",
                        "game_state": game_state.serialize_for_api()
                    }, status=400)

                game_state.award_miles -= 2000
                game_state.days_remaining -= 1
                if is_turbulent:
                    game_state.morale -= 20
                    turn_message = f"You flew to {next_loc.name}, but heavy turbulence ruined your ability to work on the plane."
                else:
                    game_state.morale = min(100, game_state.morale + 5)
                    turn_message = f"You used miles for a smooth flight to {next_loc.name}. The lounge access boosted your morale."

            game_state.current_location = next_loc

        # --- STATIONARY ACTIONS ---
        elif action == 'rest':
            game_state.morale = min(100, game_state.morale + 40)
            game_state.cash -= 150
            game_state.days_remaining -= 1
            turn_message = "You took a day off to hit the beach and recharge. Morale is up, but your wallet took a hit."

        elif action == 'code':
            game_state.bugs = max(0, game_state.bugs - 30)
            game_state.morale -= 15
            game_state.days_remaining -= 1
            turn_message = "You locked yourself in the hotel room and crushed some technical debt. Bugs are down, but you are exhausted."

        elif action == 'mentor':
            game_state.days_remaining -= 1
            game_state.morale = min(100, game_state.morale + 20)
            # Explaining concepts helps you debug!
            game_state.bugs = max(0, game_state.bugs - 10)
            turn_message = "You hosted a meetup for local devs. Teaching others helped you spot errors in your own code, and the community energy felt great!"

        else:
            return JsonResponse({"error": "Unknown action."}, status=400)

        # ==========================================
        # 3. Random Events (The spice of life and the game!)
        # ==========================================
        event_roll = random.randint(1, 100)

        if event_roll <= 8:
            game_state.bugs += 15
            turn_message += " A silent dependency update broke your staging environment! (+15 Bugs)"

        elif 8 < event_roll <= 16:
            game_state.cash -= 150
            turn_message += " You dropped your laptop charger in the sand and had to buy an overpriced replacement. (-$150)"

        elif 16 < event_roll <= 24:
            game_state.award_miles += 5000
            turn_message += " You flexed your AAdvantage knowledge. A previous flight delay finally paid out a compensation claim! (+5,000 Miles)"

        elif 24 < event_roll <= 32:
            game_state.days_remaining -= 1
            game_state.morale -= 10
            turn_message += " You tried to optimize your route, but over-engineered it like a Ferrari pit wall strategy. You lost a day."

        elif 32 < event_roll <= 40:
            game_state.morale += 25
            turn_message += " You found a local pub showing the Chelsea match. Against all odds, they actually secured 3 points! (+25 Morale)"

        elif 40 < event_roll <= 48:
            game_state.bugs += 20
            game_state.morale -= 10
            turn_message += " Chelsea just signed another 45 players and the transfer API crashed. You stayed up all night reading the logs. (+20 Bugs)"

        elif 48 < event_roll <= 56:
            game_state.days_remaining -= 1
            game_state.morale += 15
            turn_message += " The hostel's Wi-Fi was flat. You spent the day setting up VLANs and firewall rules to sandbox their IoT devices. (-1 Day, +15 Morale)"

        elif 56 < event_roll <= 64:
            game_state.cash -= 100
            game_state.morale = min(100, game_state.morale + 30)
            turn_message += " You stumbled into a Bilt Dining experience. The pescatarian seafood tasting menu was incredible, but pricey. (-$100, Max Morale)"

        elif 64 < event_roll <= 72:
            game_state.days_remaining -= 1
            game_state.morale = 100
            turn_message += " It's Carnival season! The entire island is a DDoS attack of sound and color. You couldn't work, but your soul is healed. (-1 Day, Morale at 100%)"

        elif 72 < event_roll <= 80:
            game_state.bugs = max(0, game_state.bugs - 25)
            turn_message += " A local politician cut the ribbon on a new submarine fiber cable. With single-digit ping, you destroyed your ticket backlog. (-25 Bugs)"

        elif 80 < event_roll <= 88:
            game_state.bugs = max(0, game_state.bugs - 15)
            game_state.award_miles += 1000
            turn_message += " You successfully tunneled into your home Raspberry Pi to bypass a regional IP block. Flawless execution. (-15 Bugs, +1,000 Miles)"

        elif 88 < event_roll <= 95:
            game_state.cash -= 50
            game_state.morale += 10
            turn_message += " A local go-kart track was hosting an F1 watch party. You optimized their timing system in exchange for drinks. (-$50, +10 Morale)"

        else:  # 96-100 (The rare jackpot)
            game_state.cash += 1000
            turn_message += " You met a rogue Angel Investor on a catamaran. They loved your elevator pitch and wired you a micro-grant! (+$1,000)"

        # ==========================================
        # 4. SAVE AND RETURN
        # ==========================================
        game_state.save()

        return JsonResponse({
            "message": turn_message,
            "game_state": game_state.serialize_for_api()
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
