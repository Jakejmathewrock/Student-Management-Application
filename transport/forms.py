from django import forms
from .models import BusRoute, Driver, Vehicle, TransportFee, VehicleMaintenance, DailyTripLog


class BusRouteForm(forms.ModelForm):
    """Form for creating and updating bus routes"""
    
    class Meta:
        model = BusRoute
        fields = [
            'route_number', 'route_name', 'start_point', 'end_point',
            'total_distance', 'estimated_duration', 'departure_time',
            'return_time', 'stops_list', 'status'
        ]
        widgets = {
            'route_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., RT-001'
            }),
            'route_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Route name'
            }),
            'start_point': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Starting location'
            }),
            'end_point': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Final destination'
            }),
            'total_distance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'estimated_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in minutes'
            }),
            'departure_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'return_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'stops_list': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter each stop on a new line'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class DriverForm(forms.ModelForm):
    """Form for creating and updating driver details"""
    
    class Meta:
        model = Driver
        fields = [
            'driver_id', 'full_name', 'phone', 'email', 'address',
            'date_of_birth', 'blood_group', 'license_number', 'license_type',
            'license_issue_date', 'license_expiry_date', 'date_of_joining',
            'salary', 'status', 'assigned_route', 'photo',
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'driver_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., DRV-001'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'blood_group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A+'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'License number'
            }),
            'license_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'license_issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'license_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_of_joining': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_route': forms.Select(attrs={
                'class': 'form-control'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact phone'
            }),
        }


class VehicleForm(forms.ModelForm):
    """Form for creating and updating vehicle details"""
    
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_number', 'vehicle_type', 'make_model', 'manufacturing_year',
            'seating_capacity', 'chassis_number', 'engine_number', 'fuel_type',
            'mileage', 'registration_date', 'registration_expiry',
            'insurance_number', 'insurance_expiry', 'fitness_certificate_number',
            'fitness_expiry', 'status', 'current_route', 'assigned_driver',
            'gps_enabled', 'gps_device_id', 'current_odometer', 'photo'
        ]
        widgets = {
            'vehicle_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., KA-01-AB-1234'
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'make_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Tata Starbus'
            }),
            'manufacturing_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2020'
            }),
            'seating_capacity': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'chassis_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Chassis number'
            }),
            'engine_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Engine number'
            }),
            'fuel_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'registration_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'registration_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'insurance_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Insurance number'
            }),
            'insurance_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fitness_certificate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fitness certificate number'
            }),
            'fitness_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'current_route': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_driver': forms.Select(attrs={
                'class': 'form-control'
            }),
            'gps_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'gps_device_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'GPS device ID'
            }),
            'current_odometer': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


class TransportFeeForm(forms.ModelForm):
    """Form for managing transport fees"""
    
    class Meta:
        model = TransportFee
        fields = [
            'student', 'route', 'fee_amount', 'paid_amount', 'discount',
            'academic_year', 'semester', 'status', 'payment_method',
            'transaction_id', 'paid_date', 'due_date', 'remarks'
        ]
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-control'
            }),
            'route': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fee_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'paid_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'academic_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2024-25'
            }),
            'semester': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Transaction ID'
            }),
            'paid_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class VehicleMaintenanceForm(forms.ModelForm):
    """Form for vehicle maintenance records"""
    
    class Meta:
        model = VehicleMaintenance
        fields = [
            'vehicle', 'maintenance_type', 'description', 'scheduled_date',
            'completed_date', 'cost', 'status', 'mechanic_name', 'remarks'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={
                'class': 'form-control'
            }),
            'maintenance_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'completed_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'mechanic_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mechanic name'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class DailyTripLogForm(forms.ModelForm):
    """Form for daily trip logs"""
    
    class Meta:
        model = DailyTripLog
        fields = [
            'route', 'vehicle', 'driver', 'trip_date', 'departure_time',
            'arrival_time', 'starting_odometer', 'ending_odometer',
            'status', 'remarks'
        ]
        widgets = {
            'route': forms.Select(attrs={
                'class': 'form-control'
            }),
            'vehicle': forms.Select(attrs={
                'class': 'form-control'
            }),
            'driver': forms.Select(attrs={
                'class': 'form-control'
            }),
            'trip_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'departure_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'arrival_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'starting_odometer': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'ending_odometer': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }