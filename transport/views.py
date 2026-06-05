from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from .models import BusRoute, Driver, Vehicle, TransportFee, VehicleMaintenance, DailyTripLog
from .forms import (
    BusRouteForm, DriverForm, VehicleForm, TransportFeeForm,
    VehicleMaintenanceForm, DailyTripLogForm
)
from students.models import Student


# ═══════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════

@login_required
def transport_dashboard(request):
    """Transport management dashboard"""
    context = {
        'total_routes': BusRoute.objects.count(),
        'active_routes': BusRoute.objects.filter(status='active').count(),
        'total_vehicles': Vehicle.objects.count(),
        'active_vehicles': Vehicle.objects.filter(status='active').count(),
        'total_drivers': Driver.objects.count(),
        'active_drivers': Driver.objects.filter(status='active').count(),
        'total_students_using_transport': TransportFee.objects.values('student').distinct().count(),
        'pending_fees': TransportFee.objects.filter(status__in=['pending', 'partial']).count(),
        'overdue_fees': TransportFee.objects.filter(status='overdue').count(),
        'upcoming_maintenance': VehicleMaintenance.objects.filter(status='scheduled').count(),
        'recent_trips': DailyTripLog.objects.all()[:5],
    }
    return render(request, 'transport/dashboard.html', context)


# ═══════════════════════════════════════════════════════════════
#  BUS ROUTES
# ═══════════════════════════════════════════════════════════════

@login_required
def route_list(request):
    """List all bus routes"""
    query = request.GET.get('query', '').strip()
    status = request.GET.get('status', '').strip()
    
    routes = BusRoute.objects.all().annotate(
        vehicle_count=Count('vehicles'),
        driver_count=Count('drivers')
    )
    
    if query:
        routes = routes.filter(
            Q(route_number__icontains=query) |
            Q(route_name__icontains=query) |
            Q(start_point__icontains=query) |
            Q(end_point__icontains=query)
        )
    if status:
        routes = routes.filter(status=status)
        
    return render(request, 'transport/route_list.html', {
        'routes': routes,
        'query': query,
        'selected_status': status,
    })


@login_required
def route_add(request):
    """Add new bus route"""
    if request.method == 'POST':
        form = BusRouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus route created successfully!')
            return redirect('route_list')
    else:
        form = BusRouteForm()
    return render(request, 'transport/route_form.html', {'form': form, 'title': 'Add Bus Route'})


@login_required
def route_edit(request, pk):
    """Edit bus route"""
    route = get_object_or_404(BusRoute, pk=pk)
    if request.method == 'POST':
        form = BusRouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus route updated successfully!')
            return redirect('route_list')
    else:
        form = BusRouteForm(instance=route)
    return render(request, 'transport/route_form.html', {'form': form, 'title': 'Edit Bus Route', 'route': route})


@login_required
def route_delete(request, pk):
    """Delete bus route"""
    route = get_object_or_404(BusRoute, pk=pk)
    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Bus route deleted successfully!')
        return redirect('route_list')
    return render(request, 'transport/route_confirm_delete.html', {'route': route})


@login_required
def route_detail(request, pk):
    """Bus route detail view"""
    route = get_object_or_404(BusRoute, pk=pk)
    vehicles = route.vehicles.all()
    drivers = route.drivers.all()
    students = Student.objects.filter(transport_fees__route=route).distinct()
    return render(request, 'transport/route_detail.html', {
        'route': route,
        'vehicles': vehicles,
        'drivers': drivers,
        'students': students
    })


# ═══════════════════════════════════════════════════════════════
#  DRIVERS
# ═══════════════════════════════════════════════════════════════

@login_required
def driver_list(request):
    """List all drivers"""
    query = request.GET.get('query', '').strip()
    status = request.GET.get('status', '').strip()
    route_id = request.GET.get('route', '').strip()
    
    drivers = Driver.objects.all().select_related('assigned_route')
    
    if query:
        drivers = drivers.filter(
            Q(full_name__icontains=query) |
            Q(driver_id__icontains=query) |
            Q(phone__icontains=query)
        )
    if status:
        drivers = drivers.filter(status=status)
    if route_id:
        drivers = drivers.filter(assigned_route_id=route_id)
        
    routes = BusRoute.objects.filter(status='active')
    return render(request, 'transport/driver_list.html', {
        'drivers': drivers,
        'query': query,
        'selected_status': status,
        'selected_route': route_id,
        'routes': routes,
    })


@login_required
def driver_add(request):
    """Add new driver"""
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver added successfully!')
            return redirect('driver_list')
    else:
        form = DriverForm()
    return render(request, 'transport/driver_form.html', {'form': form, 'title': 'Add Driver'})


@login_required
def driver_edit(request, pk):
    """Edit driver"""
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES, instance=driver)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver updated successfully!')
            return redirect('driver_list')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'transport/driver_form.html', {'form': form, 'title': 'Edit Driver', 'driver': driver})


@login_required
def driver_delete(request, pk):
    """Delete driver"""
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        driver.delete()
        messages.success(request, 'Driver deleted successfully!')
        return redirect('driver_list')
    return render(request, 'transport/driver_confirm_delete.html', {'driver': driver})


@login_required
def driver_detail(request, pk):
    """Driver detail view"""
    driver = get_object_or_404(Driver, pk=pk)
    vehicles = driver.vehicles.all()
    trips = DailyTripLog.objects.filter(driver=driver)[:10]
    return render(request, 'transport/driver_detail.html', {
        'driver': driver,
        'vehicles': vehicles,
        'trips': trips
    })


# ═══════════════════════════════════════════════════════════════
#  VEHICLES
# ═══════════════════════════════════════════════════════════════

@login_required
def vehicle_list(request):
    """List all vehicles"""
    query = request.GET.get('query', '').strip()
    status = request.GET.get('status', '').strip()
    route_id = request.GET.get('route', '').strip()
    
    vehicles = Vehicle.objects.all().select_related('current_route', 'assigned_driver')
    
    if query:
        vehicles = vehicles.filter(
            Q(vehicle_number__icontains=query) |
            Q(make_model__icontains=query) |
            Q(vehicle_type__icontains=query)
        )
    if status:
        vehicles = vehicles.filter(status=status)
    if route_id:
        vehicles = vehicles.filter(current_route_id=route_id)
        
    routes = BusRoute.objects.filter(status='active')
    return render(request, 'transport/vehicle_list.html', {
        'vehicles': vehicles,
        'query': query,
        'selected_status': status,
        'selected_route': route_id,
        'routes': routes,
    })


@login_required
def vehicle_add(request):
    """Add new vehicle"""
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle added successfully!')
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'transport/vehicle_form.html', {'form': form, 'title': 'Add Vehicle'})


@login_required
def vehicle_edit(request, pk):
    """Edit vehicle"""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully!')
            return redirect('vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'transport/vehicle_form.html', {'form': form, 'title': 'Edit Vehicle', 'vehicle': vehicle})


@login_required
def vehicle_delete(request, pk):
    """Delete vehicle"""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted successfully!')
        return redirect('vehicle_list')
    return render(request, 'transport/vehicle_confirm_delete.html', {'vehicle': vehicle})


@login_required
def vehicle_detail(request, pk):
    """Vehicle detail view"""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    maintenance_records = VehicleMaintenance.objects.filter(vehicle=vehicle)
    trips = DailyTripLog.objects.filter(vehicle=vehicle)[:10]
    return render(request, 'transport/vehicle_detail.html', {
        'vehicle': vehicle,
        'maintenance_records': maintenance_records,
        'trips': trips
    })


# ═══════════════════════════════════════════════════════════════
#  TRANSPORT FEES
# ═══════════════════════════════════════════════════════════════

@login_required
def transport_fee_list(request):
    """List all transport fees"""
    fees = TransportFee.objects.all().select_related('student', 'route')
    
    # Filters
    query = request.GET.get('query', '').strip()
    status = request.GET.get('status')
    route_id = request.GET.get('route')
    
    if query:
        fees = fees.filter(
            Q(student__full_name__icontains=query) |
            Q(student__roll_number__icontains=query)
        )
    if status:
        fees = fees.filter(status=status)
    if route_id:
        fees = fees.filter(route_id=route_id)
    
    routes = BusRoute.objects.filter(status='active')
    
    # Summary
    total_collected = fees.filter(status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    from django.db.models import F, ExpressionWrapper, DecimalField
    total_pending = fees.filter(status__in=['pending', 'partial', 'overdue']).aggregate(
        total=Sum(ExpressionWrapper(F('fee_amount') - F('discount') - F('paid_amount'), output_field=DecimalField()))
    )['total'] or 0
    
    context = {
        'fees': fees,
        'routes': routes,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'selected_status': status,
        'selected_route': route_id,
        'query': query,
    }
    return render(request, 'transport/fee_list.html', context)


@login_required
def transport_fee_add(request):
    """Add new transport fee"""
    if request.method == 'POST':
        form = TransportFeeForm(request.POST)
        if form.is_valid():
            fee = form.save(commit=False)
            # Auto-update status based on payment
            if fee.paid_amount >= fee.fee_amount:
                fee.status = 'paid'
            elif fee.paid_amount > 0:
                fee.status = 'partial'
            fee.save()
            messages.success(request, 'Transport fee record created successfully!')
            return redirect('transport_fee_list')
    else:
        form = TransportFeeForm()
    
    routes = BusRoute.objects.filter(status='active')
    students = Student.objects.filter(status='active')
    
    return render(request, 'transport/fee_form.html', {
        'form': form,
        'title': 'Add Transport Fee',
        'routes': routes,
        'students': students
    })


@login_required
def transport_fee_edit(request, pk):
    """Edit transport fee"""
    fee = get_object_or_404(TransportFee, pk=pk)
    if request.method == 'POST':
        form = TransportFeeForm(request.POST, instance=fee)
        if form.is_valid():
            fee = form.save(commit=False)
            # Auto-update status based on payment
            if fee.paid_amount >= fee.fee_amount:
                fee.status = 'paid'
            elif fee.paid_amount > 0:
                fee.status = 'partial'
            fee.save()
            messages.success(request, 'Transport fee updated successfully!')
            return redirect('transport_fee_list')
    else:
        form = TransportFeeForm(instance=fee)
    return render(request, 'transport/fee_form.html', {'form': form, 'title': 'Edit Transport Fee', 'fee': fee})


@login_required
def transport_fee_delete(request, pk):
    """Delete transport fee"""
    fee = get_object_or_404(TransportFee, pk=pk)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, 'Transport fee record deleted successfully!')
        return redirect('transport_fee_list')
    return render(request, 'transport/fee_confirm_delete.html', {'fee': fee})


@login_required
def transport_fee_detail(request, pk):
    """Transport fee detail view"""
    fee = get_object_or_404(TransportFee, pk=pk)
    return render(request, 'transport/fee_detail.html', {'fee': fee})


# ═══════════════════════════════════════════════════════════════
#  VEHICLE MAINTENANCE
# ═══════════════════════════════════════════════════════════════

@login_required
def maintenance_list(request):
    """List all maintenance records with search & filters"""
    query = request.GET.get('query', '').strip()
    status = request.GET.get('status', '').strip()
    m_type = request.GET.get('type', '').strip()
    
    maintenance = VehicleMaintenance.objects.all().select_related('vehicle')
    
    if query:
        maintenance = maintenance.filter(
            Q(vehicle__vehicle_number__icontains=query) |
            Q(mechanic_name__icontains=query) |
            Q(description__icontains=query)
        )
    if status:
        maintenance = maintenance.filter(status=status)
    if m_type:
        maintenance = maintenance.filter(maintenance_type=m_type)
        
    return render(request, 'transport/maintenance_list.html', {
        'maintenance': maintenance,
        'query': query,
        'selected_status': status,
        'selected_type': m_type,
        'status_choices': VehicleMaintenance.STATUS_CHOICES,
        'type_choices': VehicleMaintenance.MAINTENANCE_TYPE_CHOICES,
    })


@login_required
def maintenance_add(request):
    """Add new maintenance record"""
    if request.method == 'POST':
        form = VehicleMaintenanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance record created successfully!')
            return redirect('maintenance_list')
    else:
        form = VehicleMaintenanceForm()
    return render(request, 'transport/maintenance_form.html', {'form': form, 'title': 'Add Maintenance Record'})


@login_required
def maintenance_edit(request, pk):
    """Edit maintenance record"""
    maintenance = get_object_or_404(VehicleMaintenance, pk=pk)
    if request.method == 'POST':
        form = VehicleMaintenanceForm(request.POST, instance=maintenance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance record updated successfully!')
            return redirect('maintenance_list')
    else:
        form = VehicleMaintenanceForm(instance=maintenance)
    return render(request, 'transport/maintenance_form.html', {'form': form, 'title': 'Edit Maintenance Record', 'maintenance': maintenance})


@login_required
def maintenance_delete(request, pk):
    """Delete maintenance record"""
    maintenance = get_object_or_404(VehicleMaintenance, pk=pk)
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, 'Maintenance record deleted successfully!')
        return redirect('maintenance_list')
    return render(request, 'transport/maintenance_confirm_delete.html', {'maintenance': maintenance})


# ═══════════════════════════════════════════════════════════════
#  DAILY TRIP LOGS
# ═══════════════════════════════════════════════════════════════

@login_required
def trip_log_list(request):
    """List all trip logs"""
    trips = DailyTripLog.objects.all().select_related('route', 'vehicle', 'driver')
    
    # Filters
    date = request.GET.get('date')
    route_id = request.GET.get('route')
    status = request.GET.get('status')
    
    if date:
        trips = trips.filter(trip_date=date)
    if route_id:
        trips = trips.filter(route_id=route_id)
    if status:
        trips = trips.filter(status=status)
    
    routes = BusRoute.objects.filter(status='active')
    
    context = {
        'trips': trips,
        'routes': routes,
        'selected_date': date,
        'selected_route': route_id,
        'selected_status': status,
    }
    return render(request, 'transport/trip_log_list.html', context)


@login_required
def trip_log_add(request):
    """Add new trip log"""
    if request.method == 'POST':
        form = DailyTripLogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trip log created successfully!')
            return redirect('trip_log_list')
    else:
        form = DailyTripLogForm()
    
    routes = BusRoute.objects.filter(status='active')
    vehicles = Vehicle.objects.filter(status='active')
    drivers = Driver.objects.filter(status='active')
    
    return render(request, 'transport/trip_log_form.html', {
        'form': form,
        'title': 'Add Trip Log',
        'routes': routes,
        'vehicles': vehicles,
        'drivers': drivers
    })


@login_required
def trip_log_edit(request, pk):
    """Edit trip log"""
    trip = get_object_or_404(DailyTripLog, pk=pk)
    if request.method == 'POST':
        form = DailyTripLogForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trip log updated successfully!')
            return redirect('trip_log_list')
    else:
        form = DailyTripLogForm(instance=trip)
    
    routes = BusRoute.objects.filter(status='active')
    vehicles = Vehicle.objects.filter(status='active')
    drivers = Driver.objects.filter(status='active')
    
    return render(request, 'transport/trip_log_form.html', {
        'form': form,
        'title': 'Edit Trip Log',
        'trip': trip,
        'routes': routes,
        'vehicles': vehicles,
        'drivers': drivers
    })


@login_required
def trip_log_delete(request, pk):
    """Delete trip log"""
    trip = get_object_or_404(DailyTripLog, pk=pk)
    if request.method == 'POST':
        trip.delete()
        messages.success(request, 'Trip log deleted successfully!')
        return redirect('trip_log_list')
    return render(request, 'transport/trip_log_confirm_delete.html', {'trip': trip})


@login_required
def trip_log_detail(request, pk):
    """Trip log detail view"""
    trip = get_object_or_404(DailyTripLog, pk=pk)
    return render(request, 'transport/trip_log_detail.html', {'trip': trip})


# ─── Transport PDF Report Generators ─────────────────────────

@login_required
def transport_fee_receipt_pdf(request, pk):
    fee = get_object_or_404(TransportFee, pk=pk)
    # Check permissions (student or admin)
    if not request.user.is_staff:
        try:
            student = Student.objects.get(email=request.user.email)
            if fee.student != student:
                raise PermissionDenied
        except Student.DoesNotExist:
            raise PermissionDenied

    import io
    from decimal import Decimal
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<font size=20><b>EduAdmin Transport Services</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=11 color='#06B6D4'>Official Transport Fee Receipt</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#06B6D4')))
    elements.append(Spacer(1, 0.4*cm))

    details = [
        ['Receipt ID', f'TR-FEE-{fee.pk}', 'Date Issued', fee.updated_at.strftime('%d %b %Y')],
        ['Student Name', fee.student.full_name, 'Roll Number', fee.student.roll_number],
        ['Assigned Route', str(fee.route), 'Academic Year', fee.academic_year],
        ['Payment Method', fee.get_payment_method_display() or '—', 'Transaction ID', fee.transaction_id or '—'],
        ['Payment Status', fee.get_status_display(), 'Due Date', fee.due_date.strftime('%d %b %Y') if fee.due_date else '—'],
    ]
    dt = Table(details, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#ECFEFF')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#ECFEFF')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(dt)
    elements.append(Spacer(1, 0.6*cm))

    elements.append(Paragraph("<b>Fee Summary Details</b>", styles['Heading3']))
    fee_data = [
        ['Description', 'Amount (₹)'],
        ['Base Transport Fee', f"{fee.fee_amount:.2f}"],
        ['Discount Applied', f"{fee.discount:.2f}"],
        ['Amount Paid', f"{fee.paid_amount:.2f}"],
        ['Outstanding Balance Due', f"{fee.balance_due():.2f}"],
    ]
    ft = Table(fee_data, colWidths=[12*cm, 5*cm])
    ft.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#06B6D4')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ECFEFF')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 7),
    ]))
    elements.append(ft)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0')))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(
        "<font size=8 color='#64748B'>This is a computer-generated transport receipt and does not require a physical signature. "
        "For transport queries, contact: transport@eduadmin.edu</font>",
        ParagraphStyle('footer', alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Transport_Receipt_{fee.pk}.pdf"'
    return response


@login_required
def transport_fee_export_pdf(request):
    if not request.user.is_staff:
        raise PermissionDenied

    fees = TransportFee.objects.all().select_related('student', 'route')
    
    status = request.GET.get('status')
    route_id = request.GET.get('route')
    if status:
        fees = fees.filter(status=status)
    if route_id:
        fees = fees.filter(route_id=route_id)

    import io
    from decimal import Decimal
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<font size=18><b>Transport Fee Collection Report</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=10 color='#64748B'>Campus Transport Department — Financial Report</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#06B6D4')))
    elements.append(Spacer(1, 0.4*cm))

    table_data = [['Student', 'Roll No', 'Route', 'Fee (₹)', 'Paid (₹)', 'Due (₹)', 'Status']]
    total_fee = Decimal('0')
    total_paid = Decimal('0')
    total_due = Decimal('0')
    
    for f in fees:
        due = f.balance_due()
        table_data.append([
            f.student.full_name,
            f.student.roll_number,
            f.route.route_number if f.route else '—',
            f"{f.fee_amount:.1f}",
            f"{f.paid_amount:.1f}",
            f"{due:.1f}",
            f.get_status_display()
        ])
        total_fee += f.fee_amount
        total_paid += f.paid_amount
        total_due += due
        
    table_data.append([
        'Total Summary', '', '',
        f"₹{total_fee:.1f}", f"₹{total_paid:.1f}", f"₹{total_due:.1f}", ''
    ])

    t = Table(table_data, colWidths=[4*cm, 2.3*cm, 2.2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#06B6D4')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ECFEFF')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Transport_Fees_Report.pdf"'
    return response


@login_required
def route_export_pdf(request):
    """Export all bus routes as a PDF directory"""
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    routes = BusRoute.objects.all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph("<font size=18><b>Campus Bus Routes Directory</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=10 color='#64748B'>Campus Transport Department — Route Configurations</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#06B6D4')))
    elements.append(Spacer(1, 0.4*cm))

    # Table data
    data = [['Route No', 'Route Name', 'Start Point', 'End Point', 'Departure', 'Monthly Fee']]
    for r in routes:
        data.append([
            r.route_number,
            r.route_name,
            r.start_point,
            r.end_point,
            r.departure_time.strftime('%H:%M') if r.departure_time else '—',
            f"₹{r.monthly_fee:.0f}" if r.monthly_fee else '—'
        ])

    t = Table(data, colWidths=[2.5*cm, 4*cm, 4*cm, 4*cm, 2*cm, 1.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#06B6D4')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Bus_Routes_Directory.pdf"'
    return response