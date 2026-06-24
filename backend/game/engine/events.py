import random
from typing import Any, List
from .constants import RANDOM_EVENTS, EVENT_THRESHOLDS, EVENT_MODIFIERS


def trigger_random_event(game: Any, location_name: str) -> str:
    """
    Selects a dynamically weighted random event and applies its impacts.
    """
    calculated_weights: List[int] = []

    for event in RANDOM_EVENTS:
        weight: int = event["base_weight"]
        if game.morale < EVENT_THRESHOLDS["MORALE_LOW"] and event["type"] == "negative":
            weight += EVENT_MODIFIERS["LOW_MORALE_PENALTY"]
        elif game.morale >= EVENT_THRESHOLDS["MORALE_HIGH"] and event["type"] == "positive":
            weight += EVENT_MODIFIERS["HIGH_MORALE_BONUS"]
        calculated_weights.append(weight)

    selected_event = random.choices(RANDOM_EVENTS, weights=calculated_weights, k=1)[0]

    for stat, change_value in selected_event.get("impacts", {}).items():
        if hasattr(game, stat):
            current_value = getattr(game, stat)
            setattr(game, stat, current_value + change_value)
        else:
            print(f"Warning: Game state has no attribute '{stat}'")

    return f"Random Event: {selected_event['text']}"
