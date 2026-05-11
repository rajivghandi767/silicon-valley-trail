import random
from .constants import RANDOM_EVENTS


def trigger_random_event(game, location_name):
    """
    Selects a dynamically weighted random event and applies its impacts to the game state.
    """
    # 1. Adjust weights dynamically based on player morale (Feedback Loop)
    calculated_weights = []
    for event in RANDOM_EVENTS:
        weight = event["base_weight"]
        if game.morale < 30 and event["type"] == "negative":
            weight += 25  # Death spiral: Low morale makes bad things more likely
        elif game.morale >= 80 and event["type"] == "positive":
            weight += 10  # Momentum: High morale makes good things more likely
        calculated_weights.append(weight)

    # 2. Roll the loaded dice using Binary Search on Prefix Sums
    selected_event = random.choices(
        RANDOM_EVENTS, weights=calculated_weights, k=1)[0]

    # 3. Apply the impacts dynamically
    for stat, change_value in selected_event.get("impacts", {}).items():
        if hasattr(game, stat):
            current_value = getattr(game, stat)
            setattr(game, stat, current_value + change_value)
        else:
            print(f"Warning: Game state has no attribute '{stat}'")

    return f"Random Event: {selected_event['text']}"
