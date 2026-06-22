from enum import StrEnum
from typing import Dict, Any, List, Set

"""
Game Engine Constants & Configuration
This module decouples all mathematical impacts, thresholds, and narrative strings 
from the core Python logic to ensure a highly scalable, data-driven architecture.
"""

# ============================================================================
# 1. CORE ENGINE MECHANICS, ACTIONS & ECONOMY
# ============================================================================

WARNING_THRESHOLDS = {
    "DAYS": 3,
    "CASH": 300,
    "MILES": 2000,
    "MORALE": 30,
    "BUGS_WARNING": 30,
    "BUGS_CRITICAL": 40,
}


class GameAction(StrEnum):
    """Strict enumeration of all valid player actions."""

    # Stationary
    REST = "rest"
    CODE = "code"
    MENTOR = "mentor"

    # Travel
    FERRY = "travel_ferry"
    FLIGHT = "travel_flight"


# Using sets for O(1) constant time membership checking
STATIONARY_ACTIONS: Set[GameAction] = {
    GameAction.REST,
    GameAction.CODE,
    GameAction.MENTOR,
}
TRAVEL_ACTIONS: Set[GameAction] = {GameAction.FERRY, GameAction.FLIGHT}
# --- Action Impacts on Player State ---
STATIONARY_ACTION_IMPACTS: Dict[GameAction, Dict[str, int]] = {
    GameAction.REST: {"morale": 40, "cash": -100, "days_remaining": -1},
    GameAction.CODE: {"bugs": -20, "morale": -20, "days_remaining": -1},
    GameAction.MENTOR: {"bugs": -10, "morale": 20, "days_remaining": -1},
}

TRAVEL_IMPACTS: Dict[str, Any] = {
    "flight_cost_threshold": 2000,
    "ferry_success": {"cash": -150, "morale": -10, "days_remaining": -1},
    "ferry_grounded": {"morale": -20, "days_remaining": -1},
    "flight_cost": {"award_miles": -2000, "days_remaining": -1},
    "flight_smooth": {"morale": 10},
    "flight_turbulent": {"morale": -15},
    "flight_grounded": {"morale": -15, "days_remaining": -1},
}

# --- Data-Driven Random Events ---
RANDOM_EVENTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "type": "negative",
        "base_weight": 10,
        "text": "A silent React dependency update broke your staging environment! (+20 Bugs)",
        "impacts": {"bugs": 20},
    },
    {
        "id": 2,
        "type": "negative",
        "base_weight": 10,
        "text": "You left your laptop charger at TSA and had to buy an overpriced replacement. (-$150)",
        "impacts": {"cash": -150},
    },
    {
        "id": 3,
        "type": "negative",
        "base_weight": 10,
        "text": "You over-engineered your API architecture. You lost a day rewriting it. (-1 Day, -10 Morale)",
        "impacts": {"days_remaining": -1, "morale": -10},
    },
    {
        "id": 4,
        "type": "positive",
        "base_weight": 10,
        "text": "You found an expat bar showing the Chelsea match. They secured 3 points! (+25 Morale)",
        "impacts": {"morale": 25},
    },
    {
        "id": 5,
        "type": "positive",
        "base_weight": 10,
        "text": "A new submarine fiber cable provided single-digit ping. You destroyed your backlog. (-20 Bugs)",
        "impacts": {"bugs": -20},
    },
    {
        "id": 6,
        "type": "positive",
        "base_weight": 10,
        "text": "A delayed flight finally paid out AAdvantage compensation! (+2000 Miles)",
        "impacts": {"award_miles": 2000},
    },
    {
        "id": 7,
        "type": "negative",
        "base_weight": 10,
        "text": "Imposter syndrome hit hard after reviewing a Senior Engineer's portfolio. (-20 Morale)",
        "impacts": {"morale": -20},
    },
    {
        "id": 8,
        "type": "negative",
        "base_weight": 10,
        "text": "You accidentally pushed your .env file to GitHub. You spent a day rotating keys. (-1 Day, +15 Bugs)",
        "impacts": {"bugs": 15, "days_remaining": -1},
    },
    {
        "id": 9,
        "type": "positive",
        "base_weight": 10,
        "text": "You helped a local dive shop fix their booking database. They paid you in cash! (+$500)",
        "impacts": {"cash": 500},
    },
    {
        "id": 10,
        "type": "positive",
        "base_weight": 10,
        "text": "You connected with a REACH Alumni on LinkedIn who reviewed your PRs! (-15 Bugs, +15 Morale)",
        "impacts": {"bugs": -15, "morale": 15},
    },
    {
        "id": 11,
        "type": "negative",
        "base_weight": 10,
        "text": "You stumbled into a Bilt Dining experience. The pescatarian menu was incredible! (-$120, +30 Morale)",
        "impacts": {"cash": -120, "morale": 30},
    },
    {
        "id": 12,
        "type": "negative",
        "base_weight": 10,
        "text": "Carnival season! A DDoS attack of sound and color. You couldn't work at all. (-1 Day)",
        "impacts": {"days_remaining": -1},
    },
]


# ============================================================================
# 2. NARRATIVE & STORY STRINGS
# ============================================================================

INTRO_MESSAGE: str = (
    "Traditional application portals are a black hole. As a self-taught developer from New York, you need a different strategy to land your dream Backend Apprenticeship.\n\n"
    "Word on the wire is that Shalini Agarwal, Senior Director of Engineering at LinkedIn and head of the REACH program, is taking a rare, unplugged vacation to attend the Nature Island Hiking Festival in Dominica 🇩🇲.\n\n"
    "You have 18 Days, your laptop, a little bit of cash, and a stash of airline award miles.\n\n"
    "YOUR MISSION: Island-hop your way from NYC down the Caribbean chain to Dominica.\n\n"
    "Manage your resources, navigate real-time tropical weather, keep your morale high, and ensure your code is bug-free so you can deliver a flawless pitch!\n\n"
    "// THE JOURNEY BEGINS IN NEW YORK CITY 🇺🇸. TO GET STARTED, CHOOSE AN ACTION BELOW ..."
)

REBOOT_MESSAGE: str = (
    "// GAME RESTART SEQUENCE INITIATED...\n"
    "// MEMORY CLEARED. SECURE BACKEND API CONNECTION RE-ESTABLISHED.\n\n"
    "> SHALINI (LinkedIn REACH): Rough run, but failure is just data. Let's try this again.\n\n"
    + INTRO_MESSAGE
)

SESSION_RESTORED_MESSAGE: str = (
    "// SECURE SESSION RESTORED...\n"
    "// RESUMING AT STOP {stop_number}: {location_name}\n\n"
    "// Awaiting your next command..."
)

VICTORY_MESSAGE: str = (
    "🏆 VICTORY: YOU SURVIVED THE TRAIL!\n"
    "You reached {location_name} and delivered a flawless pitch! Your apprenticeship awaits.\n\n"
    "> [ FINAL STATS ]\n"
    "  - Days to Spare: {days_remaining}\n"
    "  - Remaining Cash: ${cash}\n"
    "  - Remaining Miles: {miles}\n"
    "  - Morale: {morale}%\n"
    "  - Bugs: {bugs}"
)

# --- Turn-by-Turn Narrative Logs ---
ACTION_BASE_MESSAGES: Dict[GameAction, str] = {
    GameAction.REST: "> You took a day off to hit the beach and recharge.\n\n> Result:\n  - Wallet depleted (-$100)\n  - Time elapsed (-1 Day)",
    GameAction.CODE: "> You locked yourself in the hotel room and crushed some technical debt. (-1 Day)",
    GameAction.MENTOR: "> You hosted a meetup for local devs. Teaching others helped you spot errors in your own code! (-1 Day)",
}

TRAVEL_MESSAGES: Dict[str, str] = {
    "ferry_sea_conditions": "> Sea Conditions: {wave_height}m waves.\n\n",
    "ferry_grounded": "> Result: SMALL CRAFT ADVISORY! Ferries grounded. (-1 Day)",
    "ferry_success": "> Safely made it to {location_name}. (-$150, -1 Day)",
    "flight_insufficient_miles": "Insufficient Award Miles.",
    "flight_grounded": "> Result: ATC GROUND STOP! Flights canceled. (-1 Day)",
    "flight_turbulent": "> Result: Landed in {location_name}, awful flight. (-2000 Miles, -1 Day)",
    "flight_smooth": "> Result: Smooth flight to {location_name}. (-2000 Miles, -1 Day)",
    "error_no_location": "No next location found.",
    "error_invalid_action": "Invalid action sequence requested.",
}

# ============================================================================
# 3. UI & STATUS MESSAGES
# ============================================================================

STATUS_WON: str = "MISSION ACCOMPLISHED. Secure connection closed."
STATUS_LOST: str = "SYSTEM FAILURE. Secure connection closed."
STATUS_ACTIVE: str = "Currently in {location_name} with ${cash} cash, {award_miles} miles, {morale}% morale, {bugs} bugs, and {days_remaining} days remaining."

DEFEAT_MESSAGES: Dict[str, str] = {
    "time": "💀 FATAL EXCEPTION: You ran out of days or it is mathematically impossible to reach Dominica in time.",
    "bankrupt": "💀 FATAL EXCEPTION: You went bankrupt and ran out of miles. You are stranded in the Caribbean.",
    "bugs": "💀 FATAL EXCEPTION: Your MVP crashed during the pitch. The codebase was overwhelmed with 50+ bugs.",
    "morale": "💀 FATAL EXCEPTION: Burnout. Your morale hit 0 and you closed your laptop for good.",
}
