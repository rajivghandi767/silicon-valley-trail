# backend/game/engine/constants.py

"""
Game Engine Constants & Configuration
This module decouples all mathematical impacts, thresholds, and narrative strings 
from the core Python logic to ensure a highly scalable, data-driven architecture.
"""

# ============================================================================
# 1. CORE ENGINE MECHANICS & ECONOMY
# ============================================================================

# --- Initial Game State & Bounds ---
INITIAL_STATE = {
    "cash": 2500,
    "award_miles": 8000,
    "morale": 100,
    "bugs": 0,
    "days_remaining": 18
}

TOTAL_JOURNEY_STOPS = 10
MAX_ALLOWED_BUGS = 50
MAX_MORALE = 100

# --- Game Weather API Constants ---
API_TIMEOUT_SECONDS = 3

# Marine Conditions
SMALL_CRAFT_WAVE_HEIGHT_M = 1.5
BASE_ROUGH_SEAS_PROB = 0.20

# Aviation Conditions
WMO_THUNDERSTORM_MIN_CODE = 61
TURBULENCE_WIND_SPEED_KMH = 25.0
BASE_THUNDERSTORM_PROB = 0.20
BASE_TURBULENCE_PROB = 0.50

# --- Action Impacts on Player State ---
STATIONARY_ACTION_IMPACTS = {
    'rest': {'morale': 40, 'cash': -100, 'days_remaining': -1},
    'code': {'bugs': -10, 'morale': -20, 'days_remaining': -1},
    'mentor': {'bugs': -10, 'morale': 20, 'days_remaining': -1},
}

TRAVEL_IMPACTS = {
    'flight_cost_threshold': 2000,
    'ferry_success': {'cash': -150, 'morale': -10, 'days_remaining': -1},
    'ferry_grounded': {'morale': -20, 'days_remaining': -1},
    'flight_cost': {'award_miles': -2000, 'days_remaining': -1},
    'flight_smooth': {'morale': 10},
    'flight_turbulent': {'morale': -15},
    'flight_grounded': {'morale': -15, 'days_remaining': -1},
}

# --- Data-Driven Random Events ---
# Dynamically weighted in events.py based on player morale (Feedback Loop)
RANDOM_EVENTS = [
    {
        "id": 1, "type": "negative", "base_weight": 10,
        "text": "A silent React dependency update broke your staging environment! (+20 Bugs)",
        "impacts": {"bugs": 20}
    },
    {
        "id": 2, "type": "negative", "base_weight": 10,
        "text": "You left your laptop charger at TSA and had to buy an overpriced replacement. (-$150)",
        "impacts": {"cash": -150}
    },
    {
        "id": 3, "type": "negative", "base_weight": 10,
        "text": "You over-engineered your API architecture. You lost a day rewriting it. (-1 Day, -10 Morale)",
        "impacts": {"days_remaining": -1, "morale": -10}
    },
    {
        "id": 4, "type": "positive", "base_weight": 10,
        "text": "You found an expat bar showing the Chelsea match. They secured 3 points! (+25 Morale)",
        "impacts": {"morale": 25}
    },
    {
        "id": 5, "type": "positive", "base_weight": 10,
        "text": "A new submarine fiber cable provided single-digit ping. You destroyed your backlog. (-20 Bugs)",
        "impacts": {"bugs": -20}
    },
    {
        "id": 6, "type": "positive", "base_weight": 10,
        "text": "A delayed flight finally paid out AAdvantage compensation! (+2000 Miles)",
        "impacts": {"award_miles": 2000}
    },
    {
        "id": 7, "type": "negative", "base_weight": 10,
        "text": "Imposter syndrome hit hard after reviewing a Senior Engineer's portfolio. (-20 Morale)",
        "impacts": {"morale": -20}
    },
    {
        "id": 8, "type": "negative", "base_weight": 10,
        "text": "You accidentally pushed your .env file to GitHub. You spent a day rotating keys. (-1 Day, +15 Bugs)",
        "impacts": {"bugs": 15, "days_remaining": -1}
    },
    {
        "id": 9, "type": "positive", "base_weight": 10,
        "text": "You helped a local dive shop fix their booking database. They paid you in cash! (+$500)",
        "impacts": {"cash": 500}
    },
    {
        "id": 10, "type": "positive", "base_weight": 10,
        "text": "You connected with a REACH Alumni on LinkedIn who reviewed your PRs! (-15 Bugs, +15 Morale)",
        "impacts": {"bugs": -15, "morale": 15}
    },
    {
        "id": 11, "type": "negative", "base_weight": 10,
        "text": "You stumbled into a Bilt Dining experience. The pescatarian menu was incredible! (-$120, +30 Morale)",
        "impacts": {"cash": -120, "morale": 30}
    },
    {
        "id": 12, "type": "negative", "base_weight": 10,
        "text": "Carnival season! A DDoS attack of sound and color. You couldn't work at all. (-1 Day)",
        "impacts": {"days_remaining": -1}
    }
]


# ============================================================================
# 2. NARRATIVE & STORY STRINGS
# ============================================================================

INTRO_MESSAGE = (
    "Traditional application portals are a black hole. As a self-taught developer from New York, you need a different strategy to land your dream Backend Apprenticeship.\n\n"
    "Word on the wire is that Shalini Agarwal, Senior Director of Engineering at LinkedIn and head of the REACH program, is taking a rare, unplugged vacation to attend the Nature Island Hiking Festival in Dominica 🇩🇲.\n\n"
    "You have 18 Days, your laptop, a little bit of cash, and a stash of airline award miles.\n\n"
    "YOUR MISSION: Island-hop your way from NYC down the Caribbean chain to Dominica.\n\n"
    "Manage your resources, navigate real-time tropical weather, keep your morale high, and ensure your code is bug-free so you can deliver a flawless pitch!\n\n"
    "// THE JOURNEY BEGINS IN NEW YORK CITY 🇺🇸. TO GET STARTED, CHOOSE AN ACTION BELOW ..."
)

REBOOT_MESSAGE = (
    "// GAME RESTART SEQUENCE INITIATED...\n"
    "// MEMORY CLEARED. SECURE BACKEND API CONNECTION RE-ESTABLISHED.\n\n"
    "> SHALINI (LinkedIn REACH): Rough run, but failure is just data. Let's try this again.\n\n"
    + INTRO_MESSAGE
)

SESSION_RESTORED_MESSAGE = (
    "// SECURE SESSION RESTORED...\n"
    "// RESUMING AT STOP {stop_number}: {location_name}\n\n"
    "// Awaiting your next command..."
)

VICTORY_MESSAGE = (
    "🏆 VICTORY: YOU SURVIVED THE TRAIL!\n"
    "You reached Dominica 🇩🇲 and delivered a flawless pitch to Shalini! Your apprenticeship awaits.\n\n"
    "> [ FINAL STATS ]\n"
    "  - Days to Spare: {days_remaining}\n"
    "  - Remaining Cash: ${cash}\n"
    "  - Award Miles: {miles}\n"
    "  - Final Morale: {morale}%\n"
    "  - Pitch Bugs: {bugs}"
)

# --- Turn-by-Turn Narrative Logs ---
ACTION_BASE_MESSAGES = {
    'rest': "> You took a day off to hit the beach and recharge.\n\n> Result:\n  - Wallet depleted (-$100)\n  - Time elapsed (-1 Day)",
    'code': "> You locked yourself in the hotel room and crushed some technical debt. (-1 Day)",
    'mentor': "> You hosted a meetup for local devs. Teaching others helped you spot errors in your own code! (-1 Day)"
}

TRAVEL_MESSAGES = {
    'ferry_sea_conditions': "> Sea Conditions: {wave_height}m waves.\n\n",
    'ferry_grounded': "> Result: SMALL CRAFT ADVISORY! Ferries grounded. (-1 Day)",
    'ferry_success': "> Safely made it to {location_name}. (-$150, -1 Day)",

    'flight_insufficient_miles': "Insufficient Award Miles.",
    'flight_grounded': "> Result: ATC GROUND STOP! Flights canceled. (-1 Day)",
    'flight_turbulent': "> Result: Landed in {location_name}, awful flight. (-2000 Miles, -1 Day)",
    'flight_smooth': "> Result: Smooth flight to {location_name}. (-2000 Miles, -1 Day)",

    'error_no_location': "No next location found.",
    'error_invalid_action': "Invalid action sequence requested."
}


# ============================================================================
# 3. UI & STATUS MESSAGES
# ============================================================================

STATUS_WON = "MISSION ACCOMPLISHED. Secure connection closed."
STATUS_LOST = "SYSTEM FAILURE. Secure connection closed."
STATUS_ACTIVE = "Currently in {location_name} with ${cash} cash, {award_miles} miles, {morale}% morale, {bugs} bugs, and {days_remaining} days remaining."

DEFEAT_MESSAGES = {
    "time": "💀 FATAL EXCEPTION: You ran out of days or it is mathematically impossible to reach Dominica in time.",
    "bankrupt": "💀 FATAL EXCEPTION: You went bankrupt and ran out of miles. You are stranded in the Caribbean.",
    "bugs": "💀 FATAL EXCEPTION: Your MVP crashed during the pitch. The codebase was overwhelmed with 50+ bugs.",
    "morale": "💀 FATAL EXCEPTION: Burnout. Your morale hit 0 and you closed your laptop for good."
}
