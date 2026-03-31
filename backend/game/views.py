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

            wave_height = data.get('current', {}).get('wave_height', 0.0)

            print(
                f"🌊 MARINE API SUCCESS - Waves: {wave_height}m at Lat:{latitude}")

            is_rough_seas = wave_height >= 1.5 or random.random() < 0.40
            return is_rough_seas, wave_height

            return is_rough_seas, wave_height

    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"❌ Marine API Error: {e}")
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

            print(
                f"✈️ AVIATION API SUCCESS - Wind: {wind_speed}km/h, Code: {weather_code}")

            is_thunderstorm = weather_code >= 61 or random.random() < 0.40

            is_turbulent = wind_speed >= 25.0 or random.random() < 0.50

            return is_thunderstorm, is_turbulent

    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"❌ Aviation API Error: {e}")
        # Fail open: assume clear skies
        return random.random() < 0.40, random.random() < 0.50

# ==========================================
# ENDPOINT 1: Get the current game state
# ==========================================


@require_http_methods(["GET"])
def get_state(request):
    game_state = GameState.objects.first()
    if not game_state:
        return JsonResponse({"error": "No active game found. Start a new game."}, status=404)

    # 1. Check if user refreshed AFTER winning
    if game_state.check_win_condition():
        display_message = (
            "🏆 VICTORY: YOU SURVIVED THE TRAIL!\n"
            "You reached Dominica 🇩🇲 and delivered a flawless pitch to Shalini! Your LinkedIn REACH Apprenticeship awaits.\n\n"
            "> [ FINAL STATS ]\n"
            f"  - Days to Spare: {game_state.days_remaining}\n"
            f"  - Remaining Cash: ${game_state.cash}\n"
            f"  - Award Miles: {game_state.award_miles}\n"
            f"  - Final Morale: {game_state.morale}%\n"
            f"  - Pitch Bugs: {game_state.bugs}"
        )

    # 2. Check if user refreshed AFTER losing
    elif game_state.current_location.sequence_in_journey == 1 and game_state.days_remaining == 18:
        display_message = (
            "Traditional application portals are a black hole. As a self-taught developer from New York, you need a different strategy to land your dream Backend Apprenticeship.\n\n"
            "Word on the wire is that Shalini Agarwal, Senior Director of Engineering at LinkedIn and head of the REACH program, is taking a rare, unplugged vacation to attend the Nature Island Hiking Festival in Dominica 🇩🇲.\n\n"
            "You have 18 Days, your laptop, a little bit of cash, and a stash of airline award miles.\n\n"
            "YOUR MISSION: Island-hop your way from NYC down the Caribbean chain to Dominica.\n\n"
            "Manage your resources, navigate real-time tropical weather, keep your morale high, and ensure your code is bug-free so you can deliver a flawless pitch!\n\n"
            "// Awaiting your command..."
        )

    # 4. If user is mid-game, just restore the session
    else:
        display_message = (
            "// SECURE SESSION RESTORED...\n"
            f"// RESUMING AT STOP {game_state.current_location.sequence_in_journey}: {game_state.current_location.name.upper()}\n\n"
            "// Awaiting your next command..."
        )

    response_data = game_state.serialize_for_api()
    response_data["message"] = display_message
    return JsonResponse(response_data)

# =========================================================
# ENDPOINT 2: Take an action (travel, rest, code, mentor)
# =========================================================


@csrf_exempt
@require_http_methods(["POST"])
def take_action(request):
    game_state = GameState.objects.first()
    if not game_state:
        return JsonResponse({"error": "No active game found. Start a new game."}, status=404)
    if game_state.check_loss_condition() or game_state.check_win_condition():
        return JsonResponse({
            "error": "The game has ended. Please restart.",
            "game_state": game_state.serialize_for_api()
        }, status=200)

    try:
        data = json.loads(request.body)
        action = data.get("action")

        action_names = {
            'code': 'write code', 'mentor': 'mentor local devs', 'rest': 'rest',
            'travel_ferry': 'take the ferry', 'travel_flight': 'take a flight'
        }
        turn_message = f"> You elected to {action_names.get(action, action)}.\n\n"

        successful_travel = False
        next_location = None

        old_morale = game_state.morale
        old_bugs = game_state.bugs

        # --- STATIONARY ACTIONS (NO RANDOM EVENTS) ---
        if action == 'rest':
            game_state.morale = min(100, game_state.morale + 40)
            game_state.cash -= 100
            game_state.days_remaining -= 1
            turn_message += "> You took a day off to hit the beach and recharge.\n\n> Result:\n  - Wallet depleted (-$100)\n  - Time elapsed (-1 Day)"
            if (game_state.morale - old_morale) > 0:
                turn_message += f"\n  - Morale restored (+{game_state.morale - old_morale})"

        elif action == 'code':
            game_state.bugs = max(0, game_state.bugs - 10)
            game_state.morale -= 20
            game_state.days_remaining -= 1
            turn_message += "> You locked yourself in the hotel room and crushed some technical debt.\n\n> Result:\n  - Mental exhaustion (-20 Morale)\n  - Time elapsed (-1 Day)"
            if (old_bugs - game_state.bugs) > 0:
                turn_message += f"\n  - Technical debt crushed (-{old_bugs - game_state.bugs} Bugs)"

        elif action == 'mentor':
            game_state.days_remaining -= 1
            game_state.morale = min(100, game_state.morale + 20)
            game_state.bugs = max(0, game_state.bugs - 10)
            turn_message += "> You hosted a meetup for local devs. Teaching others helped you spot errors in your own code!\n\n> Result:\n  - Time elapsed (-1 Day)"
            if (game_state.morale - old_morale) > 0:
                turn_message += f"\n  - Community karma (+{game_state.morale - old_morale} Morale)"
            if (old_bugs - game_state.bugs) > 0:
                turn_message += f"\n  - Bugs squashed via teaching (-{old_bugs - game_state.bugs} Bugs)"

        # --- TRAVEL ACTIONS (TRIGGERS RANDOM EVENTS) ---
        elif action in ['travel_ferry', 'travel_flight']:
            next_location = Location.objects.filter(
                sequence_in_journey=game_state.current_location.sequence_in_journey + 1).first()
            if not next_location:
                return JsonResponse({"message": "You are already at the final destination!", "game_state": game_state.serialize_for_api()}, status=200)

            if action == 'travel_ferry':
                is_rough_seas, wave_height = check_marine_conditions(
                    next_location.latitude, next_location.longitude)
                turn_message += f"> Sea Conditions: {wave_height}m wave height detected.\n\n"
                if is_rough_seas:
                    game_state.morale -= 20
                    game_state.days_remaining -= 1
                    turn_message += f"> Result:\n  - SMALL CRAFT ADVISORY! Ferries grounded.\n  - Travel delays (-20 Morale)\n  - Still in {game_state.current_location.name} (-1 Day)"
                else:
                    game_state.cash -= 150
                    game_state.morale -= 10
                    game_state.days_remaining -= 1
                    game_state.current_location = next_location
                    successful_travel = True
                    turn_message = f"> You took the ferry and safely made it to {next_location.name}. The sea breeze was nice, but the trip was exhausting.\n\n> Result:\n  - Funds deducted (-$150)\n  - Travel fatigue (-10 Morale)\n  - Time elapsed (-1 Day)"

            elif action == 'travel_flight':
                if game_state.award_miles < 2000:
                    turn_message += "> Insufficient Award Miles. Transaction declined."
                    return JsonResponse({"message": turn_message, "game_state": game_state.serialize_for_api()}, status=200)

                is_thunderstorm, is_turbulent = check_aviation_conditions(
                    next_location.latitude, next_location.longitude)
                if is_thunderstorm:
                    game_state.morale -= 15
                    game_state.days_remaining -= 1
                    turn_message += f"> Flight Conditions: Thunderstorms detected!\n\n> Result:\n  - ATC GROUND STOP! Flights canceled.\n  - Travel delays (-15 Morale)\n  - Still in {game_state.current_location.name} (-1 Day)"
                else:
                    game_state.award_miles -= 2000
                    game_state.days_remaining -= 1
                    game_state.current_location = next_location
                    successful_travel = True

                    if is_turbulent:
                        game_state.morale -= 15
                        turn_message += f"> Flight Conditions: High winds & turbulence.\n\n> Result:\n  - Landed in {next_location.name}, but flight was awful.\n  - Miles redeemed (-2000)\n  - Travel fatigue (-15 Morale)\n  - Time elapsed (-1 Day)"
                    else:
                        game_state.morale = min(100, game_state.morale + 10)
                        turn_message += f"> Flight Conditions: Clear skies.\n\n> Result:\n  - Smooth flight to {next_location.name}. Lounge access helped.\n  - Miles redeemed (-2000)\n  - Time elapsed (-1 Day)"
                        if (game_state.morale - old_morale) > 0:
                            turn_message += f"\n  - Lounge access boosted morale (+{game_state.morale - old_morale})"

            # ==========================================
            # RANDOM EVENTS (ONLY HAPPENS AFTER TRAVEL)
            # ==========================================
            if successful_travel and next_location:
                event_roll = random.randint(1, 12)
                event_text = ""

                ev_old_morale = game_state.morale
                ev_old_bugs = game_state.bugs

                if event_roll == 1:
                    game_state.bugs += 20
                    event_text = "A silent React dependency update broke your staging environment! (+20 Bugs)"
                elif event_roll == 2:
                    game_state.cash -= 150
                    event_text = "You left your laptop charger at TSA and had to buy an overpriced replacement. (-$150)"
                elif event_roll == 3:
                    game_state.days_remaining -= 1
                    game_state.morale -= 10
                    event_text = "You over-engineered your API architecture. You lost a day rewriting it. (-1 Day, -10 Morale)"
                elif event_roll == 4:
                    game_state.morale = min(100, game_state.morale + 25)
                    delta = game_state.morale - ev_old_morale
                    event_text = f"You found an expat bar showing the Chelsea match. They secured 3 points! (+{delta} Morale)" if delta > 0 else "Chelsea won, but you're already maxed out on good vibes."
                elif event_roll == 5:
                    game_state.bugs = max(0, game_state.bugs - 20)
                    delta = ev_old_bugs - game_state.bugs
                    event_text = f"A new submarine fiber cable provided single-digit ping. You destroyed your backlog. (-{delta} Bugs)" if delta > 0 else "Perfect Wi-Fi, but your code is already flawless."
                elif event_roll == 6:
                    game_state.award_miles += 2000
                    event_text = "A previous delayed flight finally paid out AAdvantage compensation! (+2000 Miles)"
                elif event_roll == 7:
                    game_state.morale -= 20
                    event_text = "Imposter syndrome hit hard after reviewing a Senior Engineer's portfolio. (-20 Morale)"
                elif event_roll == 8:
                    game_state.bugs += 15
                    game_state.days_remaining -= 1
                    event_text = "You accidentally pushed your .env file to GitHub. You spent a day rotating keys. (-1 Day, +15 Bugs)"
                elif event_roll == 9:
                    game_state.cash += 500
                    event_text = "You helped a local dive shop fix their booking database. They paid you in cash! (+$500)"
                elif event_roll == 10:
                    game_state.bugs = max(0, game_state.bugs - 15)
                    game_state.morale = min(100, game_state.morale + 15)
                    event_text = "You connected with a REACH Alumni on LinkedIn who reviewed your PRs! (Morale & Bug Boost)"
                elif event_roll == 11:
                    game_state.cash -= 120
                    game_state.morale = min(100, game_state.morale + 30)
                    event_text = "You stumbled into a Bilt Dining experience. The pescatarian menu was incredible! (-$120, Huge Morale Boost)"
                elif event_roll == 12:
                    game_state.days_remaining -= 1
                    event_text = "Carnival season! A DDoS attack of sound and color. You couldn't work at all. (-1 Day)"

                turn_message += f"\n\n> On arrival in {next_location.name}, {event_text}"

        # --- CLAMPING BLOCK ---
        # Stats never break their logical boundaries before saving
        game_state.morale = max(0, min(100, game_state.morale))
        game_state.bugs = max(0, game_state.bugs)

        game_state.save()

        # Check for Win/Loss - Display Result to User
        if game_state.check_win_condition():
            turn_message = (
                "🏆 VICTORY: YOU SURVIVED THE TRAIL!\n"
                "You reached Dominica 🇩🇲 and delivered a flawless pitch to Shalini! Your apprenticeship awaits.\n\n"
                "> [ FINAL STATS ]\n"
                f"  - Days to Spare: {game_state.days_remaining}\n"
                f"  - Remaining Cash: ${game_state.cash}\n"
                f"  - Award Miles: {game_state.award_miles}\n"
                f"  - Final Morale: {game_state.morale}%\n"
                f"  - Pitch Bugs: {game_state.bugs}"
            )
        elif game_state.check_loss_condition():
            if game_state.days_remaining <= 0:
                turn_message = "💀 FATAL EXCEPTION: You ran out of days. The festival ended before you reached Dominica."
            elif game_state.cash < 0:
                turn_message = "💀 FATAL EXCEPTION: You went bankrupt. You are stranded in the Caribbean."
            elif game_state.bugs >= 50:
                turn_message = "💀 FATAL EXCEPTION: Your MVP crashed during the pitch. The codebase was overwhelmed with 50+ bugs."
            elif game_state.morale <= 0:
                turn_message = "💀 FATAL EXCEPTION: Burnout. Your morale hit 0 and you closed your laptop for good."

        return JsonResponse({"message": turn_message, "game_state": game_state.serialize_for_api()}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ==========================================
# ENDPOINT 3: Restart the game
# ==========================================


@csrf_exempt
@require_http_methods(["POST"])
def restart_game(request):

    game_state = GameState.objects.first()
    if not game_state:
        return JsonResponse({"error": "No active game found."}, status=404)

        # Fetch the starting location (New York City)
    first_location = Location.objects.get(sequence_in_journey=1)

    # Reset all resources
    game_state.current_location = first_location
    game_state.cash = 2500
    game_state.award_miles = 8000
    game_state.morale = 100
    game_state.bugs = 0
    game_state.days_remaining = 18
    game_state.save()

    # Reboot Message
    reboot_message = (
        "// GAME RESTART SEQUENCE INITIATED...\n"
        "// MEMORY CLEARED. SECURE BACKEND API CONNECTION RE-ESTABLISHED.\n\n"
        "> SHALINI (LinkedIn REACH): Rough run, but failure is just data. Let's try this again.\n\n"
        "Traditional application portals are a black hole. As a self-taught developer from New York, you need a different strategy to land your dream Backend Apprenticeship.\n\n"
        "Word on the wire is that Shalini Agarwal, Senior Director of Engineering at LinkedIn and head of the REACH program, is taking a rare, unplugged vacation to attend the Nature Island Hiking Festival in Dominica 🇩🇲.\n\n"
        "You have 18 Days, your laptop, a little bit of cash, and a stash of airline award miles.\n\n"
        "YOUR MISSION: Island-hop your way from NYC down the Caribbean chain to Dominica.\n\n"
        "Manage your resources, navigate real-time tropical weather, keep your morale high, and ensure your code is bug-free so you can deliver a flawless pitch!\n\n"
        "// Awaiting your command..."
    )

    response_data = game_state.serialize_for_api()
    response_data["message"] = reboot_message

    return JsonResponse(response_data, status=200)
