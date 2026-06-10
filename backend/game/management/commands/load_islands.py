# backend/game/management/commands/load_islands.py
from django.core.management.base import BaseCommand
from game.models import Location
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Load initial island data into the database'

    def handle(self, *args, **options):
        Location.objects.all().delete()

        stops_along_journey = [
            {
                "name": "New York City 🇺🇸", "latitude": 40.6413, "longitude": -73.7781,
                "description": "The concrete jungle. Startup HQ and the start of the journey.",
                "reward_resource": "morale", "reward_amount": 10,
                "reward_message": "You attended a local tech mixer and expanded your professional network. (+10 Morale)"
            },
            {
                "name": "Anguilla 🇦🇮", "latitude": 18.2206, "longitude": -63.0686,
                "description": "An OECS territory that owns the '.ai' top-level domain. Their economy literally scales with the artificial intelligence boom. Pure passive income.",
                "reward_resource": "cash", "reward_amount": 250,
                "reward_message": "You consulted for an AI startup registering a local domain. Easy money! (+$250)"
            },
            {
                "name": "St. Eustatius", "latitude": 17.4890, "longitude": -62.9736,
                "description": "The original decentralized exchange. In the 1700s, this tiny free port bypassed global blockades to supply the American Revolution.",
                "reward_resource": "cash", "reward_amount": 150,
                "reward_message": "Tapping into the island's free-trade history, you flipped some crypto on a decentralized exchange. (+$150)"
            },
            {
                "name": "St. Barts 🇧🇱", "latitude": 17.9000, "longitude": -62.8333,
                "description": "French Caribbean luxury. Its notoriously steep runway requires a special pilot certification—the aviation equivalent of a Senior DevOps role.",
                "reward_resource": "morale", "reward_amount": 15,
                "reward_message": "You watched planes nail the terrifying runway landing while sipping espresso. Highly motivating! (+15 Morale)"
            },
            {
                "name": "Saba", "latitude": 17.6355, "longitude": -63.2327,
                "description": "Features the world's shortest commercial runway at just 400 meters. A masterclass in engineering within extreme hardware constraints.",
                "reward_resource": "bugs", "reward_amount": -10,
                "reward_message": "Inspired by the island's extreme hardware constraints, you optimized your bundle size. (-10 Bugs)"
            },
            {
                "name": "Nevis 🇰🇳", "latitude": 17.1534, "longitude": -62.5782,
                "description": "Birthplace of Alexander Hamilton, architect of the US financial system. A perfect spot to manifest some OG fintech energy for your Series A pitch.",
                "reward_resource": "cash", "reward_amount": 200,
                "reward_message": "Channeling Hamiltonian energy, you audited a smart contract and collected a bounty. (+$200)"
            },
            {
                "name": "Montserrat 🇲🇸", "latitude": 16.7425, "longitude": -62.1874,
                "description": "Once home to George Martin's AIR Studios where 80s rock legends recorded, until a volcano buried the capital. The ultimate lesson in catastrophic disaster recovery.",
                "reward_resource": "morale", "reward_amount": 20,
                "reward_message": "You explored the volcano zone. A sobering reminder that disaster recovery is essential. (+20 Morale)"
            },
            {
                "name": "Antigua 🇦🇬", "latitude": 17.1393, "longitude": -61.7795,
                "description": "The primary OECS aviation router. It acts as the central load balancer for regional flight traffic, boasting a highly redundant 365-beach backup system.",
                "reward_resource": "award_miles", "reward_amount": 1000,
                "reward_message": "The regional load balancer glitched, and you were compensated for the delay! (+1000 Miles)"
            },
            {
                "name": "Guadeloupe", "latitude": 16.2650, "longitude": -61.5510,
                "description": "French territory shaped like a butterfly. Powered heavily by geothermal energy and serves as a blazing-fast submarine cable and ferry hub.",
                "reward_resource": "bugs", "reward_amount": -15,
                "reward_message": "Plugged into the blazing-fast submarine cable hub. Your deployment pipeline was flawless. (-15 Bugs)"
            },
            {
                "name": "Dominica 🇩🇲", "latitude": 15.4150, "longitude": -61.3710,
                "description": "The Nature Island! Find Shalini Agarwal at the hiking festival and execute the pitch flawlessly.",
                "reward_resource": "morale", "reward_amount": 20,
                "reward_message": "You took a screen break to hike the lush trails, completely resetting your mental stack. (+20 Morale)"
            },
        ]

        list_of_stops = []

        for index, stop in enumerate(stops_along_journey):
            list_of_stops.append(Location(
                sequence_in_journey=index + 1,
                name=stop["name"],
                description=stop["description"],
                latitude=stop["latitude"],
                longitude=stop["longitude"],
                reward_resource=stop["reward_resource"],
                reward_amount=stop["reward_amount"],
                reward_message=stop["reward_message"]
            ))

        Location.objects.bulk_create(list_of_stops)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully loaded {len(list_of_stops)} islands/stops to the database via bulk_create.'
        ))
        
        # Clear cache to ensure updated locations reflect
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cleared Redis cache.'))
