import urllib.request
import json
import random

# ============================================================================
# EXTERNAL API INTEGRATION FUNCTIONS
# ============================================================================

# Objective: Minimum dependencies.
# Using the standard library's `urllib` instead of third-party packages like `requests`, guarantees a zero-friction local installation environment for reviewing engineers.


def check_marine_conditions(latitude, longitude):
    """
    Fetches real-time wave data from Open-Meteo's Marine API.
    Evaluates if sea conditions are safe enough for the player to travel via ferry.
    """

    # The dedicated Marine API endpoint requesting current wave_height in meters
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={latitude}&longitude={longitude}&current=wave_height"

    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': 'SiliconValleyTrail/1.0'})

        # Strict 3-second timeout to prevent blocking the Gunicorn worker thread if the external API is unresponsive.
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())

            # Used .get() chained with empty dictionaries to safely traverse the JSON.
            # This prevents fatal KeyErrors if the API payload structure unexpectedly changes.
            wave_height = data.get('current', {}).get('wave_height', 0.0)

            print(
                f"🌊 MARINE API SUCCESS - Waves: {wave_height}m at Lat:{latitude} Lon:{longitude}")

            # Waves >= 1.5m trigger a small craft advisory (travel delay).
            # Considering this is the Caribbean, we also introduce a base 20% probability of rough seas to ensure gameplay variability. This also adds an element of suspense to every ferry ride, as players won't know if they'll get lucky with calm seas or face delays until they attempt the action.
            is_rough_seas = wave_height >= 1.5 or random.random() < 0.20
            return is_rough_seas, wave_height

    except Exception as e:
        print(f"❌ Marine API Error: {e}")
        # Fallback Strategy:  If the API fails, timeouts, or the user is playing offline, we log the error but return a randomized fallback value so the core game loop never breaks i.e is_rough_seas = False, wave_height = 0.0 (Calm Seas are assumed).
        return False, 0.0


def check_aviation_conditions(latitude, longitude):
    """
    Fetches atmospheric weather using WMO (World Meteorological Organization) codes to determine flight safety and turbulence penalties.
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

            # As with marine conditions, we introduce base probabilities (20% for thunderstorms and 50% for turbulence) to ensure that even in good weather, there's still a chance of encountering challenges.

            # WMO Codes >= 61 indicate rain showers/thunderstorms which ground flights entirely.
            is_thunderstorm = weather_code >= 61 or random.random() < 0.20

            # High wind speeds trigger morale penalties due to heavy flight turbulence.
            is_turbulent = wind_speed >= 25.0 or random.random() < 0.50

            return is_thunderstorm, is_turbulent

    except Exception as e:
        print(f"❌ Aviation API Error: {e}")
        # Fail gracefully with a fallback that assumes clear skies and calm winds, ensuring the game remains playable even without API access.
        return False, False
