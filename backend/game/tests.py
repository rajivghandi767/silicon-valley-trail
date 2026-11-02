import json
from unittest.mock import MagicMock, patch
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from .models import Location, ReportedIssue
from .engine.constants import (
    CRITICAL_THRESHOLDS,
    MAX_REPORT_NOTE_LENGTH,
    REPORT_RATE_LIMIT_MAX,
)
from .engine.state import CacheGameState


class GameMechanicsTests(TestCase):
    def setUp(self) -> None:
        """
        Seed the database with locations and initialize a CacheGameState in the test cache.
        """
        self.client = Client()

        # Initialize session cookie
        session = self.client.session
        session["test_initialized"] = True
        session.save()
        self.cache_key = f"svt_game_{session.session_key}"

        # Clear global cache so dynamic total_stops doesn't persist across runs
        cache.clear()

        # 1. Seed Locations (exactly 10 to support dynamic is_won logic)
        Location.objects.create(
            name="New York City",
            description="The start.",
            sequence_in_journey=1,
            latitude=40.71,
            longitude=-74.00,
        )
        Location.objects.create(
            name="Washington D.C.",
            description="Stop 2.",
            sequence_in_journey=2,
            latitude=38.90,
            longitude=-77.03,
        )
        Location.objects.create(
            name="Dominica",
            description="The finish.",
            sequence_in_journey=10,
            latitude=15.41,
            longitude=-61.37,
        )

        for i in range(3, 10):
            Location.objects.create(
                name=f"Dummy Location {i}",
                description=f"Stop {i}.",
                sequence_in_journey=i,
                latitude=0.0,
                longitude=0.0,
            )

        # 2. Initialize Redis-backed CacheGameState
        self.game = CacheGameState(
            current_location_id=1,
            cash=2500,
            award_miles=8000,
            morale=100,
            bugs=0,
            days_remaining=18,
        )
        cache.set(self.cache_key, self.game, timeout=86400)

    def test_initial_state_loads(self) -> None:
        response = self.client.get(reverse("get_state"))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["cash"], 2500)
        self.assertEqual(data["current_location"], "New York City")
        self.assertEqual(data["max_bugs"], CRITICAL_THRESHOLDS["BUGS"])
        self.assertFalse(data["is_won"])

    def test_stationary_action_rest(self) -> None:
        self.game.morale = 50
        cache.set(self.cache_key, self.game, timeout=86400)

        response = self.client.post(
            reverse("take_action"),
            data=json.dumps({"action": "rest"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        # Fetch updated state from Cache
        updated_game = cache.get(self.cache_key)

        self.assertEqual(updated_game.morale, 100)
        self.assertEqual(updated_game.cash, 2400)
        self.assertEqual(updated_game.days_remaining, 17)

    @patch("game.engine.actions.check_aviation_conditions")
    @patch("game.engine.events.random.choices")
    def test_successful_flight_with_mocked_api(
        self, mock_choices: MagicMock, mock_weather: MagicMock
    ) -> None:
        # 1. Mock the Weather API
        mock_weather.return_value = (False, False)

        # 2. Mock the RNG event roll (Event #9 adds $500)
        mock_choices.return_value = [{"impacts": {"cash": 500}, "text": "Mocked Event"}]

        response = self.client.post(
            reverse("take_action"),
            data=json.dumps({"action": "travel_flight"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        updated_game = cache.get(self.cache_key)

        self.assertEqual(updated_game.current_location_id, 2)
        self.assertEqual(updated_game.award_miles, 7000)
        self.assertEqual(updated_game.cash, 3000)
        self.assertEqual(updated_game.days_remaining, 17)

    def test_fatal_exception_loss_condition(self) -> None:
        self.game.bugs = 50
        cache.set(self.cache_key, self.game, timeout=86400)

        self.assertTrue(self.game.is_lost)

        response = self.client.post(
            reverse("take_action"),
            data=json.dumps({"action": "code"}),
            content_type="application/json",
        )

        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertIn("The game has ended", data.get("error", ""))

    @patch("game.engine.actions.check_aviation_conditions")
    @patch("game.engine.events.random.choices")
    def test_victory_condition(
        self, mock_choices: MagicMock, mock_weather: MagicMock
    ) -> None:
        mock_weather.return_value = (False, False)
        mock_choices.return_value = [{"impacts": {}, "text": "Mocked Event"}]

        # We are at stop 9 (Dummy Location 9)
        self.game.current_location_id = 9
        cache.set(self.cache_key, self.game, timeout=86400)

        response = self.client.post(
            reverse("take_action"),
            data=json.dumps({"action": "travel_flight"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        updated_game = cache.get(self.cache_key)

        self.assertTrue(updated_game.is_won)

        data = json.loads(response.content)
        self.assertIn("VICTORY", data.get("message", ""))
        self.assertIn("Dominica", data.get("message", ""))

    def test_submit_report_valid_and_validation(self) -> None:
        # 1. Valid report
        valid_res = self.client.post(
            reverse("submit_report"),
            data=json.dumps({"issue_type": "ui_bug", "user_note": "Button misaligned"}),
            content_type="application/json",
        )
        self.assertEqual(valid_res.status_code, 200)
        self.assertEqual(ReportedIssue.objects.count(), 1)

        # 2. Invalid issue_type rejected
        invalid_type_res = self.client.post(
            reverse("submit_report"),
            data=json.dumps({"issue_type": "sql_injection", "user_note": "Test note"}),
            content_type="application/json",
        )
        self.assertEqual(invalid_type_res.status_code, 400)

        # 3. Empty note rejected
        empty_note_res = self.client.post(
            reverse("submit_report"),
            data=json.dumps({"issue_type": "other", "user_note": "   "}),
            content_type="application/json",
        )
        self.assertEqual(empty_note_res.status_code, 400)

        # 4. Over-length note rejected
        long_note_res = self.client.post(
            reverse("submit_report"),
            data=json.dumps(
                {"issue_type": "other", "user_note": "x" * (MAX_REPORT_NOTE_LENGTH + 1)}
            ),
            content_type="application/json",
        )
        self.assertEqual(long_note_res.status_code, 400)

    def test_submit_report_rate_limiting(self) -> None:
        cache.set("svt_report_rate_127.0.0.1", REPORT_RATE_LIMIT_MAX, timeout=3600)
        rate_limited_res = self.client.post(
            reverse("submit_report"),
            data=json.dumps({"issue_type": "typo", "user_note": "Rate limited note"}),
            content_type="application/json",
        )
        self.assertEqual(rate_limited_res.status_code, 429)
