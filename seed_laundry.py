"""Seed demo laundry orders. Run: python seed_laundry.py"""
import os, django, random, uuid
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from django.utils import timezone
from students.models import Student, LaundryService, LaundryOrder, LaundryOrderItem

students = list(Student.objects.filter(status='active')[:10])
services = list(LaundryService.objects.filter(is_available=True))
statuses = ['placed','collected','processing','ready','delivered','delivered','delivered']
blocks   = ['A', 'B', 'C', 'D']

if not students:
    print('No active students found')
else:
    added = 0
    for student in students:
        for _ in range(random.randint(2, 4)):
            status    = random.choice(statuses)
            selected  = random.sample(services, min(random.randint(2,6), len(services)))
            txn_id    = 'LDY-TXN-' + str(uuid.uuid4()).upper()[:10]
            room_no   = 'Block-' + random.choice(blocks) + '-' + str(random.randint(101, 320))
            upi_str   = student.full_name.replace(' ','').lower() + '@upi'

            order = LaundryOrder.objects.create(
                student        = student,
                status         = status,
                payment_status = 'paid',
                room_number    = room_no,
                upi_id         = upi_str,
                transaction_id = txn_id,
                paid_at        = timezone.now(),
                total_amount   = Decimal('0'),
                paid_amount    = Decimal('0'),
            )

            total = Decimal('0')
            for svc in selected:
                qty = random.randint(1, 5)
                sub = svc.price_per_item * qty
                total += sub
                LaundryOrderItem.objects.create(
                    order      = order,
                    service    = svc,
                    quantity   = qty,
                    unit_price = svc.price_per_item,
                    subtotal   = sub,
                )

            order.total_amount = total
            order.paid_amount  = total
            order.save(update_fields=['total_amount','paid_amount'])
            added += 1

    from django.db.models import Sum
    rev = LaundryOrder.objects.filter(payment_status='paid').aggregate(t=Sum('paid_amount'))['t'] or 0
    print(f'Created {added} orders.  Total orders: {LaundryOrder.objects.count()}')
    print(f'Total revenue: Rs.{rev:.0f}')
    print('Done!')
