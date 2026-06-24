from django.core.management import call_command
from django.core.management.base import BaseCommand
from game.models import Location


class Command(BaseCommand):
    help = "Seeds initial database data"

    def handle(self, *args, **kwargs):
        self.stdout.write("🧹 Wiping existing data to ensure a fresh state...")
        Location.objects.all().delete()

        self.stdout.write("Seeding island data...")
        call_command("load_islands")
        self.stdout.write(
            self.style.SUCCESS("Database seeding completed successfully.")
        )
