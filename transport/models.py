from django.db import models
from django.utils import timezone
import uuid


# ═══════════════════════════════════════════════════════════════
#  TRANSPORT MANAGEMENT MODULE
# ═══════════════════════════════════════════════════════════════

class BusRoute(models.Model):
    """Bus Route Management - Defines routes for college transport"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    route_number = models.CharField(max_length=20, unique=True, help_text="Unique route identifier (e.g., RT-001)")
    route_name = models.CharField(max_length=150, help_text="Descriptive name for the route")
    start_point = models.CharField(max_length=200, help_text="Starting location")
    end_point = models.CharField(max_length=200, help_text="Final destination")
    total_distance = models.DecimalField(max_digits=6, decimal_places=2, help_text="Total distance in KM")
    estimated_duration = models.PositiveIntegerField(help_text="Estimated duration in minutes")
    
    # Timing
    departure_time = models.TimeField(help_text="Departure time from start point")
    return_time = models.TimeField(help_text="Return time from end point")
    
    # Stops information
    stops_list = models.TextField(help_text="List of stops (one per line)")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['route_number']
        verbose_name_plural = 'Bus Routes'
    
    def __str__(self):
        return f"{self.route_number} - {self.route_name}"
    
    def stops_count(self):
        """Return number of stops in the route"""
        if self.stops_list:
            return len([s for s in self.stops_list.strip().split('\n') if s.strip()])
        return 0


class Driver(models.Model):
    """Driver Details - Information about bus drivers"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive'),
    ]
    
    LICENSE_CHOICES = [
        ('LMV', 'Light Motor Vehicle'),
        ('HMV', 'Heavy Motor Vehicle'),
        ('MCWG', 'Motor Cycle With Gear'),
    ]
    
    # Personal Information
    driver_id = models.CharField(max_length=20, unique=True, help_text="Unique driver ID")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    
    # License Information
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=10, choices=LICENSE_CHOICES, default='HMV')
    license_issue_date = models.DateField()
    license_expiry_date = models.DateField()
    
    # Employment
    date_of_joining = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Assigned Route
    assigned_route = models.ForeignKey(BusRoute, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    
    # Photo
    photo = models.ImageField(upload_to='transport/drivers/', null=True, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.driver_id})"
    
    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/img/default-driver.png'
    
    def is_license_valid(self):
        """Check if driver's license is valid"""
        from datetime import date
        return date.today() <= self.license_expiry_date


class Vehicle(models.Model):
    """Vehicle Tracking - Information about transport vehicles"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
        ('breakdown', 'Breakdown'),
    ]
    
    VEHICLE_TYPE_CHOICES = [
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('minibus', 'Mini Bus'),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('diesel', 'Diesel'),
        ('petrol', 'Petrol'),
        ('cng', 'CNG'),
        ('electric', 'Electric'),
    ]
    
    # Vehicle Information
    vehicle_number = models.CharField(max_length=20, unique=True, help_text="Registration number")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='bus')
    make_model = models.CharField(max_length=100, help_text="Make and Model (e.g., Tata Starbus)")
    manufacturing_year = models.PositiveIntegerField()
    seating_capacity = models.PositiveIntegerField(default=40)
    
    # Technical Details
    chassis_number = models.CharField(max_length=50, unique=True)
    engine_number = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='diesel')
    mileage = models.DecimalField(max_digits=6, decimal_places=2, help_text="Mileage in km/l", default=0.00)
    
    # Registration & Insurance
    registration_date = models.DateField()
    registration_expiry = models.DateField()
    insurance_number = models.CharField(max_length=50, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    
    # Fitness
    fitness_certificate_number = models.CharField(max_length=50, blank=True)
    fitness_expiry = models.DateField(null=True, blank=True)
    
    # Status & Assignment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_route = models.ForeignKey(BusRoute, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    assigned_driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')
    
    # GPS Tracking
    gps_enabled = models.BooleanField(default=False)
    gps_device_id = models.CharField(max_length=50, blank=True)
    last_gps_update = models.DateTimeField(null=True, blank=True)
    
    # Odometer
    current_odometer = models.PositiveIntegerField(help_text="Current odometer reading in KM", default=0)
    
    # Photo
    photo = models.ImageField(upload_to='transport/vehicles/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['vehicle_number']
        verbose_name_plural = 'Vehicles'
    
    def __str__(self):
        return f"{self.vehicle_number} - {self.make_model}"
    
    def is_registration_valid(self):
        """Check if vehicle registration is valid"""
        from datetime import date
        return date.today() <= self.registration_expiry
    
    def is_insurance_valid(self):
        """Check if vehicle insurance is valid"""
        from datetime import date
        if self.insurance_expiry:
            return date.today() <= self.insurance_expiry
        return False
    
    def is_fitness_valid(self):
        """Check if fitness certificate is valid"""
        from datetime import date
        if self.fitness_expiry:
            return date.today() <= self.fitness_expiry
        return False


class TransportFee(models.Model):
    """Transport Fee Management - Fee collection for transport services"""
    
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
        ('partial', 'Partial'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
    ]
    
    # Import Student model lazily to avoid circular imports
    from students.models import Student
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transport_fees')
    
    # Route Assignment
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='fee_records')
    
    # Fee Details
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total transport fee")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Discount amount if any")
    
    # Period
    academic_year = models.CharField(max_length=20, help_text="Academic year (e.g., 2024-25)")
    semester = models.CharField(max_length=20, choices=[
        ('fall', 'Fall Semester'),
        ('spring', 'Spring Semester'),
        ('annual', 'Annual'),
    ], default='annual')
    
    # Payment Details
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    
    # Remarks
    remarks = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date', '-created_at']
        unique_together = ['student', 'route', 'academic_year', 'semester']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.route.route_number} ({self.get_status_display()})"
    
    def balance_due(self):
        """Calculate remaining balance"""
        total = self.fee_amount - self.discount
        return total - self.paid_amount
    
    def is_overdue(self):
        """Check if payment is overdue"""
        from datetime import date
        return date.today() > self.due_date and self.status != 'paid'


class VehicleMaintenance(models.Model):
    """Vehicle Maintenance Records"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    MAINTENANCE_TYPE_CHOICES = [
        ('routine', 'Routine Service'),
        ('repair', 'Repair'),
        ('oil_change', 'Oil Change'),
        ('tire_change', 'Tire Change'),
        ('break_check', 'Brake Check'),
        ('engine', 'Engine Work'),
        ('other', 'Other'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    mechanic_name = models.CharField(max_length=150, blank=True)
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.get_maintenance_type_display()}"


class DailyTripLog(models.Model):
    """Daily Trip Log for tracking vehicle movements"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='trip_logs')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trip_logs')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trip_logs')
    
    trip_date = models.DateField(default=timezone.now)
    departure_time = models.TimeField()
    arrival_time = models.TimeField(null=True, blank=True)
    
    starting_odometer = models.PositiveIntegerField()
    ending_odometer = models.PositiveIntegerField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-trip_date', '-departure_time']
        unique_together = ['route', 'vehicle', 'trip_date', 'departure_time']
    
    def __str__(self):
        return f"{self.route.route_number} - {self.trip_date} ({self.departure_time})"
    
    def distance_covered(self):
        """Calculate distance covered in the trip"""
        if self.ending_odometer and self.starting_odometer:
            return self.ending_odometer - self.starting_odometer
        return 0