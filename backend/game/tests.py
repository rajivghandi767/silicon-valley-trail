from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import json
from .models import Location, GameState


class GameMechanicsTests(TestCase):
    def setUp(self):
        """
        Runs before EVERY test. We seed a fake database with locations
        and a fresh GameState so we have a clean slate every time.
        """
        self.client = Client()

        # 1. Seed the database with the first two locations and the finish line
        self.location1 = Location.objects.create(
            name="New York City", description="The start.", sequence_in_journey=1, latitude=40.71, longitude=-74.00
        )
        self.location2 = Location.objects.create(
            name="Washington D.C.", description="Stop 2.", sequence_in_journey=2, latitude=38.90, longitude=-77.03
        )
        self.location10 = Location.objects.create(
            name="Dominica", description="The finish.", sequence_in_journey=10, latitude=15.41, longitude=-61.37
        )

        # 2. Initialize a fresh game state
        self.game_state = GameState.objects.create(
            current_location=self.location1,
            cash=2500,
            award_miles=8000,
            morale=100,
            bugs=0,
            days_remaining=18
        )

    def test_initial_state_loads(self):
        """Test that the game initializes correctly and the API returns 200 OK."""
        response = self.client.get(reverse('get_state'))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['cash'], 2500)
        self.assertEqual(data['current_location'], "New York City")
        self.assertFalse(data['is_game_over'])

    def test_stationary_action_rest(self):
        """Test that resting costs cash and days, but boosts morale."""
        # Artificially lower morale first so we can test the boost
        self.game_state.morale = 50
        self.game_state.save()

        response = self.client.post(
            reverse('take_action'),
            data=json.dumps({"action": "rest"}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.game_state.refresh_from_db()  # Fetch updated data from the test database

        self.assertEqual(self.game_state.morale, 90)         # 50 + 40 boost
        # $2500 - $100 cost
        self.assertEqual(self.game_state.cash, 2400)
        self.assertEqual(self.game_state.days_remaining, 17)  # 18 - 1 day

    @patch('game.views.check_aviation_conditions')
    @patch('game.views.random.randint')
    def test_successful_flight_with_mocked_api(self, mock_randint, mock_weather):
        """
        Test flying to the next stop with mocked clear weather and a controlled event.
        This proves our code works without actually calling the Open-Meteo API.
        """
        # 1. Mock the Weather API to return (is_thunderstorm=False, is_turbulent=False)
        mock_weather.return_value = (False, False)

        # 2. Mock the RNG event roll to always hit Event #9 (+$500 Cash)
        mock_randint.return_value = 9

        response = self.client.post(
            reverse('take_action'),
            data=json.dumps({"action": "travel_flight"}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.game_state.refresh_from_db()

        # Check that we successfully moved to Stop 2
        self.assertEqual(self.game_state.current_location, self.location2)

        # Check that miles were properly deducted (8000 - 2000)
        self.assertEqual(self.game_state.award_miles, 6000)

        # Check that Event #9 correctly added $500 to our $2500 starting cash
        self.assertEqual(self.game_state.cash, 3000)

    def test_fatal_exception_loss_condition(self):
        """Test that hitting 50 bugs triggers a Game Over lock."""
        self.game_state.bugs = 50
        self.game_state.save()

        self.assertTrue(self.game_state.check_loss_condition())

        # Try to take an action while dead
        response = self.client.post(
            reverse('take_action'),
            data=json.dumps({"action": "code"}),
            content_type="application/json"
        )

        data = json.loads(response.content)
        self.assertIn("The game has ended", data.get("error", ""))
