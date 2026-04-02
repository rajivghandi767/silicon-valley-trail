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


class GameState(models.Model):
    """
    Single source of truth for an active game session.
    Tracks current location, player resources and validates wins/losses. 
    Updates as the player makes decisions and progresses through the game.
    """

    # Since I've elected to live demo the game without user accounts or authentication, the session_key field allows us to associate a game state with a specific browser session. This way, each player can have their own unique game state that persists across page reloads and browser sessions without needing to log in.
    session_key = models.CharField(max_length=40, unique=True)

    # .PROTECT ensures an active game cannot be deleted if the associated Location is deleted.
    current_location = models.ForeignKey(Location, on_delete=models.PROTECT)

    # Game Resources
    cash = models.IntegerField(
        default=2500, help_text="Cash available for ferry rides. Running out of cash before final stop results in a loss.")
    award_miles = models.IntegerField(
        default=8000, help_text="Miles available for taking flights. Running out of miles before final stop results in a loss.")
    morale = models.IntegerField(
        default=100, help_text="Player health. Reaching 0 results in a loss. Can be affected by random events and challenges at each stop.")
    bugs = models.IntegerField(
        default=0, help_text="Codebase stability. Reaching 50 results in a loss. Can be affected by random events and challenges at each stop.")
    days_remaining = models.IntegerField(
        default=18, help_text="Number of days left to complete the journey. Reaching 0 results in a loss. Each move consumes days, and certain events can also affect this.")

    """
    Win & Loss Conditions decorated as properties for cleaner more readable code. 
    """
    @property
    def is_lost(self):
        # Loss conditions: Running out of cash, miles, morale, or reaching the bug threshold or day limit.
        return self.morale <= 0 or self.bugs >= 50 or self.days_remaining <= 0 or self.cash < 0

    @property
    def is_won(self):
        # Win condition: Successfully reaching the final destination (Stop 10). Resource checks are handled by the is_lost property above.
        return self.current_location.sequence_in_journey == 10

    def serialize_for_api(self):
        """
        Opted for pure Django serialization here to minimize dependencies. 

        Converts the model to a JSON-safe dictionary so we can send it to the React frontend without needing Django REST Framework.
        """

        # Makes the sidebar status text context-aware for a more engaging user experience. Shows the current location and resources during the game, and a clear win/loss message when the game ends.
        if self.is_won:
            status_text = "MISSION ACCOMPLISHED. Secure connection closed."
        elif self.is_lost:
            status_text = "SYSTEM FAILURE. Secure connection closed."
        else:
            status_text = str(self)

        return {
            "id": self.id,
            "current_location": self.current_location.name if self.current_location else "Unknown",
            "description": self.current_location.description if self.current_location else "",
            "sequence_in_journey": self.current_location.sequence_in_journey if self.current_location else 1,
            "cash": self.cash,
            "award_miles": self.award_miles,
            "morale": self.morale,
            "bugs": self.bugs,
            "days_remaining": self.days_remaining,
            "is_lost": self.is_lost,
            "is_won": self.is_won,
            "status_summary": status_text,
        }

    @classmethod
    def reset_game(cls, starting_location, session_key):
        """
        Wipes the current state and creates a fresh one. 
        This is called when the player clicks the "Restart Game" button on the frontend, allowing them to start a new session with a clean slate.
        """

        # Wipe any existing game data
        cls.objects.filter(session_key=session_key).delete()

        # Create a fresh game state. Automatically applies all the default values from Game Resources above.
        return cls.objects.create(
            current_location=starting_location,
            session_key=session_key
        )

    def __str__(self):
        return f"Currently in {self.current_location.name} with ${self.cash} cash, {self.award_miles} miles, {self.morale}% morale, {self.bugs} bugs, and {self.days_remaining} days remaining."
