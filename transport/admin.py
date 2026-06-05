from django.contrib import admin
from .models import BusRoute, Driver, Vehicle, TransportFee, VehicleMaintenance, DailyTripLog


@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ['route_number', 'route_name', 'start_point', 'end_point', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['route_number', 'route_name', 'start_point', 'end_point']
    ordering = ['route_number']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['driver_id', 'full_name', 'phone', 'status', 'assigned_route', 'is_license_valid']
    list_filter = ['status', 'license_type', 'assigned_route']
    search_fields = ['driver_id', 'full_name', 'phone', 'license_number']
    ordering = ['-created_at']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_number', 'make_model', 'vehicle_type', 'status', 'current_route', 'assigned_driver', 'is_registration_valid']
    list_filter = ['status', 'vehicle_type', 'fuel_type', 'current_route']
    search_fields = ['vehicle_number', 'make_model', 'chassis_number', 'engine_number']
    ordering = ['vehicle_number']


@admin.register(TransportFee)
class TransportFeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'route', 'fee_amount', 'paid_amount', 'balance_due', 'status', 'due_date']
    list_filter = ['status', 'semester', 'academic_year', 'route']
    search_fields = ['student__full_name', 'student__roll_number', 'route__route_number']
    ordering = ['-due_date']
    date_hierarchy = 'due_date'


@admin.register(VehicleMaintenance)
class VehicleMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'maintenance_type', 'scheduled_date', 'cost', 'status']
    list_filter = ['status', 'maintenance_type']
    search_fields = ['vehicle__vehicle_number', 'description']
    ordering = ['-scheduled_date']
    date_hierarchy = 'scheduled_date'


@admin.register(DailyTripLog)
class DailyTripLogAdmin(admin.ModelAdmin):
    list_display = ['route', 'vehicle', 'driver', 'trip_date', 'departure_time', 'status']
    list_filter = ['status', 'trip_date']
    search_fields = ['route__route_number', 'vehicle__vehicle_number', 'driver__full_name']
    ordering = ['-trip_date', '-departure_time']
    date_hierarchy = 'trip_date'