from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('transport/', views.transport_dashboard, name='transport_dashboard'),
    
    # Bus Routes
    path('transport/routes/', views.route_list, name='route_list'),
    path('transport/routes/add/', views.route_add, name='route_add'),
    path('transport/routes/export/pdf/', views.route_export_pdf, name='route_export_pdf'),
    path('transport/routes/<int:pk>/', views.route_detail, name='route_detail'),
    path('transport/routes/<int:pk>/edit/', views.route_edit, name='route_edit'),
    path('transport/routes/<int:pk>/delete/', views.route_delete, name='route_delete'),
    
    # Drivers
    path('transport/drivers/', views.driver_list, name='driver_list'),
    path('transport/drivers/add/', views.driver_add, name='driver_add'),
    path('transport/drivers/<int:pk>/', views.driver_detail, name='driver_detail'),
    path('transport/drivers/<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('transport/drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),
    
    # Vehicles
    path('transport/vehicles/', views.vehicle_list, name='vehicle_list'),
    path('transport/vehicles/add/', views.vehicle_add, name='vehicle_add'),
    path('transport/vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('transport/vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('transport/vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),
    
    # Transport Fees
    path('transport/fees/', views.transport_fee_list, name='transport_fee_list'),
    path('transport/fees/add/', views.transport_fee_add, name='transport_fee_add'),
    path('transport/fees/<int:pk>/', views.transport_fee_detail, name='transport_fee_detail'),
    path('transport/fees/<int:pk>/pdf/', views.transport_fee_receipt_pdf, name='transport_fee_receipt_pdf'),
    path('transport/fees/report/pdf/', views.transport_fee_export_pdf, name='transport_fee_export_pdf'),
    path('transport/fees/<int:pk>/edit/', views.transport_fee_edit, name='transport_fee_edit'),
    path('transport/fees/<int:pk>/delete/', views.transport_fee_delete, name='transport_fee_delete'),
    
    # Vehicle Maintenance
    path('transport/maintenance/', views.maintenance_list, name='maintenance_list'),
    path('transport/maintenance/add/', views.maintenance_add, name='maintenance_add'),
    path('transport/maintenance/<int:pk>/edit/', views.maintenance_edit, name='maintenance_edit'),
    path('transport/maintenance/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),
    
    # Daily Trip Logs
    path('transport/trip-logs/', views.trip_log_list, name='trip_log_list'),
    path('transport/trip-logs/add/', views.trip_log_add, name='trip_log_add'),
    path('transport/trip-logs/<int:pk>/', views.trip_log_detail, name='trip_log_detail'),
    path('transport/trip-logs/<int:pk>/edit/', views.trip_log_edit, name='trip_log_edit'),
    path('transport/trip-logs/<int:pk>/delete/', views.trip_log_delete, name='trip_log_delete'),
]