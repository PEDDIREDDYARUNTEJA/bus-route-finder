from django.db import models

class Stop(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the bus stop (e.g. Ameerpet)")
    code = models.CharField(max_length=20, blank=True, null=True, help_text="Optional short code (e.g. AMP)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Bus(models.Model):
    bus_number = models.CharField(max_length=50, unique=True, help_text="Bus Number (e.g. 20, 10H, 218)")
    route_name = models.CharField(max_length=200, help_text="Short route summary (e.g. Miyapur to Secunderabad)")
    first_bus_time = models.TimeField(help_text="Time of first bus service (e.g. 05:30:00)")
    last_bus_time = models.TimeField(help_text="Time of last bus service (e.g. 22:45:00)")
    is_active = models.BooleanField(default=True, help_text="Is this bus service currently operating?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Buses"
        ordering = ['bus_number']

    def __str__(self):
        return f"Bus {self.bus_number} ({self.route_name})"

    def get_stops_sequence(self):
        """Returns ordered list of BusStop objects for this bus."""
        return list(self.bus_stops.select_related('stop').order_by('stop_order'))

    def get_route_display(self):
        """Returns string representation of full route: Stop1 -> Stop2 -> Stop3"""
        stops = self.get_stops_sequence()
        return " -> ".join([bs.stop.name for bs in stops])

    def get_formatted_first_bus(self):
        return self.first_bus_time.strftime("%I:%M %p") if self.first_bus_time else ""

    def get_formatted_last_bus(self):
        return self.last_bus_time.strftime("%I:%M %p") if self.last_bus_time else ""


class BusStop(models.Model):
    bus = models.ForeignKey(Bus, related_name='bus_stops', on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, related_name='stop_buses', on_delete=models.CASCADE)
    stop_order = models.PositiveIntegerField(help_text="Sequence index of the stop on this route (1, 2, 3...)")

    class Meta:
        ordering = ['stop_order']
        unique_together = ('bus', 'stop')

    def __str__(self):
        return f"{self.bus.bus_number} - Stop #{self.stop_order}: {self.stop.name}"
