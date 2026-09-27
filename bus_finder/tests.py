import datetime
from django.test import TestCase, Client
from django.urls import reverse
from bus_finder.models import Stop, Bus, BusStop
from bus_finder.views import get_matching_buses

class BusFinderTestCase(TestCase):
    def setUp(self):
        # Create stops
        self.stop_ameerpet = Stop.objects.create(name="Ameerpet")
        self.stop_panjagutta = Stop.objects.create(name="Panjagutta")
        self.stop_koti = Stop.objects.create(name="Koti")

        # Create Bus 20: Ameerpet (order 1) -> Koti (order 2) -> Panjagutta (order 3)
        self.bus20 = Bus.objects.create(
            bus_number="20",
            route_name="Ameerpet to Panjagutta line",
            first_bus_time=datetime.time(5, 30),
            last_bus_time=datetime.time(22, 45),
            is_active=True
        )

        BusStop.objects.create(bus=self.bus20, stop=self.stop_ameerpet, stop_order=1)
        BusStop.objects.create(bus=self.bus20, stop=self.stop_koti, stop_order=2)
        BusStop.objects.create(bus=self.bus20, stop=self.stop_panjagutta, stop_order=3)

    def test_search_ameerpet_to_panjagutta(self):
        """Should return Bus 20 when searching Ameerpet -> Panjagutta"""
        results = get_matching_buses(self.stop_ameerpet.id, self.stop_panjagutta.id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['bus_number'], "20")
        self.assertEqual(results[0]['first_bus_time'], "05:30 AM")
        self.assertEqual(results[0]['last_bus_time'], "10:45 PM")

    def test_search_reverse_direction_no_results(self):
        """Searching Panjagutta -> Ameerpet should return 0 results because direction is reversed"""
        results = get_matching_buses(self.stop_panjagutta.id, self.stop_ameerpet.id)
        self.assertEqual(len(results), 0)

    def test_home_page_status_code(self):
        client = Client()
        response = client.get(reverse('bus_finder:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find Your City Bus Route")
