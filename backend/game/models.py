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


class ReportedIssue(models.Model):
    ISSUE_TYPES = [
        ('game_logic', 'Game Logic / Math Error'),
        ('ui_bug', 'UI / Display Glitch'),
        ('typo', 'Typo / Spelling Error'),
        ('other', 'Other Exception'),
    ]
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES)
    user_note = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_issue_type_display()}] - {'Resolved' if self.resolved else 'Pending'}"
