from django.db import models


class Location(models.Model):
    """
    Represents a location (island/stop) in the game. Each location has a name, description, and its order in the journey.
    """

    name = models.CharField(
        max_length=255, help_text="The name of the island/stop along the journey.")
    description = models.TextField(
        help_text="A brief description/fun fact about the island/stop.")
    sequence_in_journey = models.IntegerField(unique=True,
                                              help_text="The order of the stop along the journey. (Eg. 1=New York (First Stop), 10=Dominica (10th & Last Stop))")

    # Location coordinates used for OpenMeteo Weather and Marine APIs for retrieving real-time weather and sea conditions to influence game events and challenges at each stop.
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        ordering = ['sequence_in_journey']

    def __str__(self):
        return f"{self.sequence_in_journey} - {self.name}"
