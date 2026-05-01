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

# Defeat Conditions
DEFEAT_TIME = "💀 FATAL EXCEPTION: You ran out of days. The festival ended before you reached Dominica."
DEFEAT_BANKRUPT = "💀 FATAL EXCEPTION: You went bankrupt. You are stranded in the Caribbean."
DEFEAT_BUGS = "💀 FATAL EXCEPTION: Your MVP crashed during the pitch. The codebase was overwhelmed with 50+ bugs."
DEFEAT_MORALE = "💀 FATAL EXCEPTION: Burnout. Your morale hit 0 and you closed your laptop for good."
