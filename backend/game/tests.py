from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import json
from .models import Location, GameState


class GameMechanicsTests(TestCase):
    def setUp(self):
        """
        setUp is utilized to guarantee database isolation. 
        A fresh game state and locations are seeded into the test database before every single test, ensuring no state leakage between test runs.
        """
        self.client = Client()

        # Force Django's test client to initialize a session cookie so it matches the views.py logic that relies on session keys to track game state.
        session = self.client.session
        session['test_initialized'] = True
        session.save()

        # 1. Seed the database with the first two locations and the last location.
        self.location1 = Location.objects.create(
            name="New York City", description="The start.", sequence_in_journey=1, latitude=40.71, longitude=-74.00
        )
        self.location2 = Location.objects.create(
            name="Washington D.C.", description="Stop 2.", sequence_in_journey=2, latitude=38.90, longitude=-77.03
        )
        self.location10 = Location.objects.create(
            name="Dominica", description="The finish.", sequence_in_journey=10, latitude=15.41, longitude=-61.37
        )

        # 2. Initialize a fresh game state tied to the test client's session key, starting at the first location with default resources.
        self.game = GameState.objects.create(
            session_key=session.session_key,
            current_location=self.location1,
            cash=2500,
            award_miles=8000,
            morale=100,
            bugs=0,
            days_remaining=18
        )

    def test_initial_state_loads(self):
        """
        Validates that the GameState model initializes default values correctly 
        and serializes them properly to the frontend client.
        """
        response = self.client.get(reverse('get_state'))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['cash'], 2500)
        self.assertEqual(data['current_location'], "New York City")
        self.assertFalse(data['is_won'])

    def test_stationary_action_rest(self):
        """
        Tests the core state machine math (resource deduction and addition).
        Verifies that 'rest' costs cash and time, but boosts morale.
        """
        # Artificially lower morale first so we can test the boost
        self.game.morale = 50
        self.game.save()

        response = self.client.post(
            reverse('take_action'),
            data=json.dumps({"action": "rest"}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.game.refresh_from_db()  # Fetch updated data from the test database

        self.assertEqual(self.game.morale, 90)          # 50 + 40 boost
        self.assertEqual(self.game.cash, 2400)          # $2500 - $100 cost
        self.assertEqual(self.game.days_remaining, 17)  # 18 - 1 day

    @patch('game.views.check_aviation_conditions')
    @patch('game.views.random.randint')
    def test_successful_flight_with_mocked_api(self, mock_randint, mock_weather):
        """
        Test flying to the next stop with mocked clear weather and a controlled event. This proves our code works without actually calling the Open-Meteo API.
        """
        # 1. Mock the Weather API to return clear skies i.e no storms, no turbulence (is_thunderstorm=False, is_turbulent=False)
        mock_weather.return_value = (False, False)

        # 2. Mock the RNG event roll to always hit Event #9 (+$500 Cash)
        mock_randint.return_value = 9

        response = self.client.post(
            reverse('take_action'),
            data=json.dumps({"action": "travel_flight"}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.game.refresh_from_db()

        # Check that we successfully moved to Stop 2
        self.assertEqual(self.game.current_location, self.location2)

        # Check that miles were properly deducted (8000 - 2000)
        self.assertEqual(self.game.award_miles, 6000)

        # Check that Event #9 correctly added $500 to our $2500 starting cash
        self.assertEqual(self.game.cash, 3000)

        # Check that time elapsed
        self.assertEqual(self.game.days_remaining, 17)

    @patch('game.views.urllib.request.urlopen')
    def test_api_fallback_on_network_failure(self, mock_urlopen):
        """Test that a complete network failure triggers the safe fallback without crashing the game loop. If the external Marine/Aviation API times out or the user loses internet, the backend catches the exception and substitutes localized RNG."""

        # Force a timeout exception at the urllib level to simulate a network failure when the game tries to check marine conditions for ferry travel.
        mock_urlopen.side_effect = Exception("Connection timed out")

        # Taking a ferry triggers check_marine_conditions which calls the external API, so we attempt that action to test the fallback.
        response = self.client.post(
            reverse('take_action'),
            data=json.dumps({"action": "travel_ferry"}),
            content_type="application/json"
        )

        # The game should still return a 200 OK and process the turn via the fallback RNG
        self.assertEqual(response.status_code, 200)

    def test_fatal_exception_loss_condition(self):
        """Test that hitting 50 bugs triggers a loss condition."""
        self.game.bugs = 50
        self.game.save()

        # Verify the model property evaluates to True when bugs reach 50
        self.assertTrue(self.game.is_lost)

        # Attempting to take an action while in a lost state should return an error message instead of processing the turn
        response = self.client.post(
            reverse('take_action'),
            data=json.dumps({"action": "code"}),
            content_type="application/json"
        )

        data = json.loads(response.content)
        # Verify the views.py logic correctly identifies the lost state and prevents further actions, returning a 400 status with an appropriate error message.
        self.assertEqual(response.status_code, 400)
        self.assertIn("The game has ended", data.get("error", ""))
