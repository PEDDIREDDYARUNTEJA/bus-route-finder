import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bus_finder.models import Stop, Bus, BusStop

class Command(BaseCommand):
    help = "Seeds database with sample bus routes, stops, and superuser."

    def handle(self, *args, **options):
        self.stdout.write("Seeding bus finder database...")

        # 1. Create Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Created admin user (username: 'admin', password: 'admin123')"))
        else:
            self.stdout.write("Admin user already exists.")

        # 2. Stops creation
        stop_names = [
            "Miyapur", "KPHP", "Kondapur", "Ameerpet", "Lingampalli", 
            "Koti", "Panjagutta", "Secunderabad", "Begumpet", "SR Nagar",
            "Erragadda", "Kukatpally", "Patancheru", "BHEL", "Chanda Nagar",
            "Jubilee Hills", "Hitech City", "Dilsukhnagar", "Charminar", "Mehdipatnam"
        ]

        stops_dict = {}
        for name in stop_names:
            stop_obj, _ = Stop.objects.get_or_create(name=name)
            stops_dict[name] = stop_obj
        
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(stops_dict)} stops."))

        # 3. Buses creation
        buses_data = [
            {
                "bus_number": "20",
                "route_name": "Miyapur - KPHP - Kondapur - Ameerpet - Lingampalli - Koti - Panjagutta - Secunderabad",
                "first_bus": datetime.time(5, 30),
                "last_bus": datetime.time(22, 45),
                "stops": ["Miyapur", "KPHP", "Kondapur", "Ameerpet", "Lingampalli", "Koti", "Panjagutta", "Secunderabad"]
            },
            {
                "bus_number": "10H",
                "route_name": "Secunderabad - Begumpet - Panjagutta - Ameerpet - SR Nagar - Erragadda - Kukatpally",
                "first_bus": datetime.time(6, 0),
                "last_bus": datetime.time(23, 0),
                "stops": ["Secunderabad", "Begumpet", "Panjagutta", "Ameerpet", "SR Nagar", "Erragadda", "Kukatpally"]
            },
            {
                "bus_number": "218",
                "route_name": "Patancheru - BHEL - Lingampalli - Chanda Nagar - Miyapur - Kukatpally - Ameerpet - Koti",
                "first_bus": datetime.time(5, 0),
                "last_bus": datetime.time(22, 30),
                "stops": ["Patancheru", "BHEL", "Lingampalli", "Chanda Nagar", "Miyapur", "Kukatpally", "Ameerpet", "Koti"]
            },
            {
                "bus_number": "47L",
                "route_name": "Secunderabad - Begumpet - Panjagutta - Ameerpet - Jubilee Hills - Hitech City - Kondapur",
                "first_bus": datetime.time(6, 15),
                "last_bus": datetime.time(22, 15),
                "stops": ["Secunderabad", "Begumpet", "Panjagutta", "Ameerpet", "Jubilee Hills", "Hitech City", "Kondapur"]
            },
            {
                "bus_number": "222",
                "route_name": "Miyapur - Kondapur - Hitech City - Gachibowli - Mehdipatnam - Koti",
                "first_bus": datetime.time(6, 0),
                "last_bus": datetime.time(21, 45),
                "stops": ["Miyapur", "Kondapur", "Hitech City", "Mehdipatnam", "Koti"]
            }
        ]

        for bus_info in buses_data:
            bus_obj, created = Bus.objects.get_or_create(
                bus_number=bus_info["bus_number"],
                defaults={
                    "route_name": bus_info["route_name"],
                    "first_bus_time": bus_info["first_bus"],
                    "last_bus_time": bus_info["last_bus"],
                    "is_active": True
                }
            )
            if not created:
                bus_obj.route_name = bus_info["route_name"]
                bus_obj.first_bus_time = bus_info["first_bus"]
                bus_obj.last_bus_time = bus_info["last_bus"]
                bus_obj.save()

            # Clear existing stops and re-assign sequence
            BusStop.objects.filter(bus=bus_obj).delete()
            for index, stop_name in enumerate(bus_info["stops"], start=1):
                if stop_name in stops_dict:
                    BusStop.objects.create(
                        bus=bus_obj,
                        stop=stops_dict[stop_name],
                        stop_order=index
                    )
            
            self.stdout.write(self.style.SUCCESS(f"Configured Bus {bus_obj.bus_number} with {len(bus_info['stops'])} stops."))

        self.stdout.write(self.style.SUCCESS("Successfully seeded database!"))
