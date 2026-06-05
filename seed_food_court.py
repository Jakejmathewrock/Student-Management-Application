"""
Seed default food court menu items.
Usage: python seed_food_court.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from students.models import FoodItem

MENU = [
    ('Veg Thali', 'Rice, dal, sabzi, roti', 'meal', '🍛', Decimal('80')),
    ('Chicken Biryani', 'Hyderabadi style portion', 'meal', '🍗', Decimal('120')),
    ('Veg Fried Rice', 'With manchurian gravy', 'meal', '🍚', Decimal('70')),
    ('Masala Dosa', 'Sambar & chutney', 'meal', '🥞', Decimal('50')),
    ('Veg Sandwich', 'Grilled, served hot', 'snack', '🥪', Decimal('45')),
    ('French Fries', 'Crispy salted', 'snack', '🍟', Decimal('40')),
    ('Samosa (2 pcs)', 'With mint chutney', 'snack', '🥟', Decimal('30')),
    ('Paneer Wrap', 'Whole wheat wrap', 'snack', '🌯', Decimal('65')),
    ('Masala Chai', 'Hot tea', 'beverage', '☕', Decimal('15')),
    ('Cold Coffee', 'Iced blended', 'beverage', '🥤', Decimal('50')),
    ('Fresh Lime Soda', 'Sweet or salted', 'beverage', '🍋', Decimal('35')),
    ('Bottled Water', '500 ml', 'beverage', '💧', Decimal('20')),
    ('Gulab Jamun', '2 pieces', 'dessert', '🍮', Decimal('35')),
    ('Ice Cream Cup', 'Vanilla / chocolate', 'dessert', '🍨', Decimal('40')),
]

created = 0
for name, desc, cat, emoji, price in MENU:
    _, is_new = FoodItem.objects.get_or_create(
        name=name,
        defaults={
            'description': desc,
            'category': cat,
            'emoji': emoji,
            'price': price,
            'is_available': True,
        },
    )
    if is_new:
        created += 1
        print(f'  + {name} - Rs.{price}')

print(f'\nDone. {created} new items added ({FoodItem.objects.count()} total).')
