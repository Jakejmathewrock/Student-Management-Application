"""
seed_transport_fees.py  —  Run with:
  venv\Scripts\python.exe seed_transport_fees.py
"""
import os, sys, django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from transport.models import BusRoute, TransportFee
from students.models import Student

students = list(Student.objects.all()[:20])
routes   = list(BusRoute.objects.all()[:5])

if not students:
    print("No students found — run seed_data.py first.")
    sys.exit(1)
if not routes:
    print("No bus routes found — create at least one route first.")
    sys.exit(1)

ACADEMIC_YEAR = '2024-25'
SEMESTER      = 'annual'
FEE_AMOUNT    = Decimal('6000.00')

import itertools
created = 0
for student, route in zip(students, itertools.cycle(routes)):
    obj, new = TransportFee.objects.get_or_create(
        student      = student,
        route        = route,
        academic_year= ACADEMIC_YEAR,
        semester     = SEMESTER,
        defaults = dict(
            fee_amount  = FEE_AMOUNT,
            paid_amount = Decimal('0.00'),
            discount    = Decimal('0.00'),
            status      = 'pending',
            due_date    = date.today() + timedelta(days=30),
        )
    )
    if new:
        created += 1
        print(f"  Created: {student.full_name} → {route.route_number}")

print(f"\nDone — {created} transport fee records created.")
