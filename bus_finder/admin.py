from django.contrib import admin
from .models import Stop, Bus, BusStop

class BusStopInline(admin.TabularInline):
    model = BusStop
    extra = 1
    autocomplete_fields = ['stop']
    ordering = ['stop_order']

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'route_name', 'first_bus_time', 'last_bus_time', 'is_active', 'get_stops_count')
    search_fields = ('bus_number', 'route_name')
    list_filter = ('is_active',)
    inlines = [BusStopInline]

    def get_stops_count(self, obj):
        return obj.bus_stops.count()
    get_stops_count.short_description = "Total Stops"

@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ('bus', 'stop_order', 'stop')
    list_filter = ('bus',)
    ordering = ('bus', 'stop_order')
