from django.db import models


class Location(models.Model):
    name = models.CharField(
        max_length=255, help_text="The name of the island.")
    description = models.TextField(
        help_text="A brief description of the island.")
    sequence_in_journey = models.IntegerField(unique=True,
                                              help_text="The order of the stop along the journey. (1=New York, 10=Dominica)")
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        ordering = ['sequence_in_journey']

    def __str__(self):
        return f"{self.sequence_in_journey} - {self.island_name}"


class GameState(models.Model):
    current_location = models.ForeignKey(Location, on_delete=models.PROTECT)

    # Game Resources
    cash = models.IntegerField(
        default=1000, help_text="The amount of cash the player has.")
    award_miles = models.IntegerField(
        default=0, help_text="The number of award miles the player has.")
    morale = models.IntegerField(
        default=100, help_text="The morale level of the player.")
    bugs = models.IntegerField(
        default=0, help_text="The number of bugs in the pitch project.")
    days_remaining = models.IntegerField(
        default=30, help_text="The number of days remaining in the game challenge.")

    def serialize_for_api(self):
        """
        Opted for pure Django serialization here to showcase skill and minimize dependencies. 

        Converts the model instance into a JSON-safe dictionary so we can send it to the React frontend without needing Django REST Framework (Standard across my portfolio projects).
        """

        return {
            "id": self.id,
            "current_location": self.current_location.name if self.current_location else "Unknown",
            "cash": self.cash,
            "award_miles": self.award_miles,
            "morale": self.morale,
            "bugs": self.bugs,
            "days_remaining": self.days_remaining
        }

    def check_loss_condition(self):
        """
        Checks if the player has lost the game based on the defined loss conditions.
        """
        return self.morale <= 0 or self.bugs >= 100 or self.days_remaining <= 0 or self.cash < 0

    def check_win_condition(self):
        """
        Checks if the player has won the game based on reaching the final location (Dominica - The Nature Isle of the Caribbean).
        """
        return self.current_location.sequence_in_journey == 10

    def __str__(self):
        return f"Currently at {self.current_location.island_name} with ${self.cash} cash, {self.award_miles} miles, {self.morale} morale, {self.bugs} bugs, and {self.days_remaining} days remaining."
