# backend/game/engine/constants.py

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

# --- Initial Game State ---
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

# --- Game Weather Constants ---
API_TIMEOUT_SECONDS = 3

# Marine
SMALL_CRAFT_WAVE_HEIGHT_M = 1.5
BASE_ROUGH_SEAS_PROB = 0.20

# Aviation
WMO_THUNDERSTORM_MIN_CODE = 61
TURBULENCE_WIND_SPEED_KMH = 25.0
BASE_THUNDERSTORM_PROB = 0.20
BASE_TURBULENCE_PROB = 0.50

# --- Action & Turn Messages ---
ACTION_BASE_MESSAGES = {
    'rest': "> You took a day off to hit the beach and recharge.\n\n> Result:\n  - Wallet depleted (-$100)\n  - Time elapsed (-1 Day)",
    'code': "> You locked yourself in the hotel room and crushed some technical debt. (-1 Day)",
    'mentor': "> You hosted a meetup for local devs. Teaching others helped you spot errors in your own code! (-1 Day)"
}

# --- Action Impacts on Player State ---
STATIONARY_ACTION_IMPACTS = {
    'rest': {'morale': 40, 'cash': -100, 'days': -1},
    'code': {'bugs': -10, 'morale': -20, 'days': -1},
    'mentor': {'bugs': -10, 'morale': 20, 'days': -1},
}

TRAVEL_IMPACTS = {
    'ferry_success': {'cash': -150, 'morale': -10, 'days': -1},
    'ferry_grounded': {'morale': -20, 'days': -1},
    'flight_cost': {'award_miles': -2000, 'days': -1},
    'flight_smooth_morale': 10,
    'flight_turbulent_morale': -15,
    'flight_grounded_morale': -15,
}

# --- Travel Messages ---
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

VICTORY_MESSAGE = (
    "🏆 VICTORY: YOU SURVIVED THE TRAIL!\n"
    "You reached Dominica 🇩🇲 and delivered a flawless pitch to Shalini! Your apprenticeship awaits.\n\n"
    "> [ FINAL STATS ]\n"
    "  - Days to Spare: {days}\n"
    "  - Remaining Cash: ${cash}\n"
    "  - Award Miles: {miles}\n"
    "  - Final Morale: {morale}%\n"
    "  - Pitch Bugs: {bugs}"
)

# --- Status Summaries ---
STATUS_WON = "MISSION ACCOMPLISHED. Secure connection closed."
STATUS_LOST = "SYSTEM FAILURE. Secure connection closed."
STATUS_ACTIVE = "Currently in {location_name} with ${cash} cash, {award_miles} miles, {morale}% morale, {bugs} bugs, and {days_remaining} days remaining."

# Dictionary mapping failure conditions to their UI messages
DEFEAT_MESSAGES = {
    "time": "💀 FATAL EXCEPTION: You ran out of days or it is mathematically impossible to reach Dominica in time.",
    "bankrupt": "💀 FATAL EXCEPTION: You went bankrupt and ran out of miles. You are stranded in the Caribbean.",
    "bugs": "💀 FATAL EXCEPTION: Your MVP crashed during the pitch. The codebase was overwhelmed with 50+ bugs.",
    "morale": "💀 FATAL EXCEPTION: Burnout. Your morale hit 0 and you closed your laptop for good."
}
