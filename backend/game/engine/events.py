# backend/game/engine/events.py
import random


def trigger_random_event(game, location_name):
    """
    Rolls a 12-sided die to determine a random event upon successful travel.
    Mutates the cached game state directly and returns the narrative string.
    """
    event_roll = random.randint(1, 12)
    event_text = ""

    if event_roll == 1:
        game.bugs += 20
        event_text = "A silent React dependency update broke your staging environment!"
    elif event_roll == 2:
        game.cash -= 150
        event_text = "You left your laptop charger at TSA and had to buy an overpriced replacement. (-$150)"
    elif event_roll == 3:
        game.days_remaining -= 1
        game.morale -= 10
        event_text = "You over-engineered your API architecture. You lost a day rewriting it. (-1 Day)"
    elif event_roll == 4:
        game.morale += 25
        event_text = "You found an expat bar showing the Chelsea match. They secured 3 points!"
    elif event_roll == 5:
        game.bugs -= 20
        event_text = "A new submarine fiber cable provided single-digit ping. You destroyed your backlog."
    elif event_roll == 6:
        game.award_miles += 2000
        event_text = "A delayed flight finally paid out AAdvantage compensation! (+2000 Miles)"
    elif event_roll == 7:
        game.morale -= 20
        event_text = "Imposter syndrome hit hard after reviewing a Senior Engineer's portfolio."
    elif event_roll == 8:
        game.bugs += 15
        game.days_remaining -= 1
        event_text = "You accidentally pushed your .env file to GitHub. You spent a day rotating keys. (-1 Day)"
    elif event_roll == 9:
        game.cash += 500
        event_text = "You helped a local dive shop fix their booking database. They paid you in cash! (+ $500)"
    elif event_roll == 10:
        game.bugs -= 15
        game.morale += 15
        event_text = "You connected with a REACH Alumni on LinkedIn who reviewed your PRs!"
    elif event_roll == 11:
        game.cash -= 120
        game.morale += 30
        event_text = "You stumbled into a Bilt Dining experience. The pescatarian menu was incredible! (-$120)"
    elif event_roll == 12:
        game.days_remaining -= 1
        event_text = "Carnival season! A DDoS attack of sound and color. You couldn't work at all. (-1 Day)"

    return f"\n\n> On arrival in {location_name}, {event_text}"
