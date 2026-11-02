# backend/game/models.py
from django.db import models
from .engine.constants import EXTERNAL_HTTP_TIMEOUT


class Location(models.Model):
    class ResourceChoices(models.TextChoices):
        MORALE = "morale", "Morale"
        CASH = "cash", "Cash"
        AWARD_MILES = "award_miles", "Award Miles"
        BUGS = "bugs", "Bugs (Reduction)"

    RESOURCE_CHOICES = ResourceChoices.choices

    name = models.CharField(
        max_length=255, help_text="The name of the island/stop along the journey."
    )
    description = models.TextField(
        help_text="A brief description/fun fact about the island/stop."
    )
    sequence_in_journey = models.IntegerField(
        unique=True, help_text="Order of the stop (1=NYC, 10=Dominica)"
    )

    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    reward_resource = models.CharField(
        max_length=50, choices=RESOURCE_CHOICES, blank=True, null=True
    )
    reward_amount = models.IntegerField(default=0)
    reward_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["sequence_in_journey"]

    def __str__(self) -> str:
        return f"{self.sequence_in_journey} - {self.name}"


class ReportedIssue(models.Model):
    class IssueTypeChoices(models.TextChoices):
        GAME_LOGIC = "game_logic", "Game Logic / Math Error"
        UI_BUG = "ui_bug", "UI / Display Glitch"
        TYPO = "typo", "Typo / Spelling Error"
        OTHER = "other", "Other Exception"

    ISSUE_TYPES = IssueTypeChoices.choices

    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES)
    user_note = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        issue_display = dict(self.ISSUE_TYPES).get(self.issue_type, self.issue_type)
        return f"[{issue_display}] - {'Resolved' if self.resolved else 'Pending'}"

    def send_notifications(self) -> bool:
        import json
        import urllib.request
        import urllib.error
        from django.conf import settings

        issue_display = dict(self.ISSUE_TYPES).get(self.issue_type, self.issue_type)
        webhook_url = getattr(settings, "DISCORD_WEBHOOK_URL", None)

        if webhook_url:
            payload = {
                "content": f"🚨 **New Bug Report** 🚨\n**Type:** {issue_display}\n**Note:** {self.user_note}"
            }
            req = urllib.request.Request(
                url=webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "SiliconValleyTrail/1.0",
                },
                method="POST",
            )
            try:
                urllib.request.urlopen(req, timeout=EXTERNAL_HTTP_TIMEOUT)
                return True
            except urllib.error.URLError as e:
                print(f"⚠️ [WEBHOOK ERROR] Failed to route to Discord: {e}")
        else:
            print(f"📄 [LOCAL LOG] Report saved: {issue_display} - {self.user_note}")
        return False
