from django.core.management.base import BaseCommand
from game.models import GameState, Location


class Command(BaseCommand):
    help = 'Load initial island data into the database'

    def handle(self, *args, **options):
        # Clear existing data.
        # Order here is deliberate since in models.py we set on_delete=models.PROTECT.
        # As such, deleting GameState first allows us to clear the game state without violating the foreign key constraint on Location.
        GameState.objects.all().delete()
        Location.objects.all().delete()

        # Create island data for the 10 stops along the journey. This could have been AI generated or API fetched, but I opted to write it myself to share interesting facts about the stops chosen and make the experience more personal and engaging.
        stops_along_journey = [
            {"name": "New York City 🇺🇸", "latitude": 40.6413, "longitude": -73.7781,
             "description": "The concrete jungle. Startup HQ and the start of the journey."},

            {"name": "Anguilla 🇦🇮", "latitude": 18.2206, "longitude": -63.0686,
                "description": "An OECS territory that owns the '.ai' top-level domain. Their economy literally scales with the artificial intelligence boom. Pure passive income."},

            # Easter Egg: OECS stands for Organization of Eastern Caribbean States, an economic bloc that includes several island nations and territories, many of which are featured as stops in the game. OECS countries use the Eastern Caribbean Dollar EC or XCD as their currency.

            {"name": "St. Eustatius", "latitude": 17.4890, "longitude": -62.9736,
             "description": "The original decentralized exchange. In the 1700s, this tiny free port bypassed global blockades to supply the American Revolution. The perfect node to secure some shadow funding."},

            {"name": "St. Barts 🇧🇱", "latitude": 17.9000, "longitude": -62.8333,
                "description": "French Caribbean luxury. Its notoriously steep runway requires a special pilot certification—the aviation equivalent of a Senior DevOps role."},

            {"name": "Saba", "latitude": 17.6355, "longitude": -63.2327,
                "description": "Features the world's shortest commercial runway at just 400 meters. A masterclass in engineering within extreme hardware constraints."},

            {"name": "Nevis 🇰🇳", "latitude": 17.1534, "longitude": -62.5782,
                "description": "Birthplace of Alexander Hamilton, architect of the US financial system. A perfect spot to manifest some OG fintech energy for your Series A pitch."},

            {"name": "Montserrat 🇲🇸", "latitude": 16.7425, "longitude": -62.1874,
                "description": "Once home to George Martin's AIR Studios where 80s rock legends recorded, until a volcano buried the capital. The ultimate lesson in catastrophic disaster recovery."},

            {"name": "Antigua 🇦🇬", "latitude": 17.1393, "longitude": -61.7795,
                "description": "The primary OECS aviation router. It acts as the central load balancer for regional flight traffic, boasting a highly redundant 365-beach backup system."},

            {"name": "Guadeloupe 🇬🇵", "latitude": 16.2650, "longitude": -61.5510,
                "description": "French territory shaped like a butterfly. Powered heavily by geothermal energy and serves as a blazing-fast submarine cable and ferry hub."},

            {"name": "Dominica 🇩🇲", "latitude": 15.4150, "longitude": -61.3710,
                "description": "The Nature Island! Find Shalini Agarwal at the hiking festival and execute the pitch flawlessly."},
        ]

        for index, stop in enumerate(stops_along_journey):
            Location.objects.create(
                sequence_in_journey=index + 1,
                name=stop["name"],
                description=stop["description"],
                latitude=stop["latitude"],
                longitude=stop["longitude"]
            )
            self.stdout.write(self.style.SUCCESS(
                f'Created stop {index + 1}: {stop["name"]}'))

        self.stdout.write(self.style.SUCCESS(
            'Successfully loaded island data and initialized game state.'))
