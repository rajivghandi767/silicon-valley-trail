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

SESSION_RESTORED_MESSAGE = (
    "// SECURE SESSION RESTORED...\n"
    "// RESUMING AT STOP {stop_number}: {location_name}\n\n"
    "// Awaiting your next command..."
)

# --- Action & Turn Messages ---
ACTION_BASE_MESSAGES = {
    'rest': "> You took a day off to hit the beach and recharge.\n\n> Result:\n  - Wallet depleted (-$100)\n  - Time elapsed (-1 Day)",
    'code': "> You locked yourself in the hotel room and crushed some technical debt. (-1 Day)",
    'mentor': "> You hosted a meetup for local devs. Teaching others helped you spot errors in your own code! (-1 Day)"
}

# Dictionary mapping failure conditions to their UI messages
DEFEAT_MESSAGES = {
    "time": "💀 FATAL EXCEPTION: You ran out of days or it is mathematically impossible to reach Dominica in time.",
    "bankrupt": "💀 FATAL EXCEPTION: You went bankrupt and ran out of miles. You are stranded in the Caribbean.",
    "bugs": "💀 FATAL EXCEPTION: Your MVP crashed during the pitch. The codebase was overwhelmed with 50+ bugs.",
    "morale": "💀 FATAL EXCEPTION: Burnout. Your morale hit 0 and you closed your laptop for good."
}
