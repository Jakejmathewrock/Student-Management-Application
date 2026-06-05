"""
Create student and parent login accounts linked to Student records.
Usage: python create_portal_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Student


# Backfill parent emails where missing
for student in Student.objects.filter(parent_email=''):
    student.parent_email = f'parent.{student.roll_number.lower().replace("-", "")}@edu.com'
    student.save(update_fields=['parent_email'])
    print(f'  set parent_email for {student.roll_number}: {student.parent_email}')


def username_from_roll(roll):
    return roll.lower().replace('-', '').replace(' ', '')


def username_from_email(email):
    local = email.split('@')[0]
    return local.replace('.', '_').replace('-', '_')[:30]


print('Creating student portal accounts...')
for student in Student.objects.all():
    uname = username_from_roll(student.roll_number)
    if User.objects.filter(username=uname).exists():
        print(f'  skip student (exists): {uname}')
        continue
    first, *rest = student.full_name.split()
    last = rest[-1] if rest else ''
    user = User.objects.create_user(
        username=uname,
        email=student.email,
        password='student123',
        first_name=first,
        last_name=last,
    )
    UserProfile.objects.create(user=user, role='student')
    print(f'  student: {uname} / student123  ({student.full_name})')

print('\nCreating parent portal accounts...')
parent_emails_done = set()
for student in Student.objects.exclude(parent_email=''):
    email = student.parent_email.strip().lower()
    if not email or email in parent_emails_done:
        continue
    uname = username_from_email(email)
    base = uname
    n = 1
    while User.objects.filter(username=uname).exists():
        uname = f'{base}{n}'
        n += 1
    if User.objects.filter(email__iexact=email, profile__role='parent').exists():
        parent_emails_done.add(email)
        print(f'  skip parent (exists): {email}')
        continue
    name = student.parent_name or 'Parent'
    parts = name.split()
    user = User.objects.create_user(
        username=uname,
        email=email,
        password='parent123',
        first_name=parts[0] if parts else 'Parent',
        last_name=parts[-1] if len(parts) > 1 else '',
    )
    UserProfile.objects.create(user=user, role='parent')
    parent_emails_done.add(email)
    print(f'  parent: {uname} / parent123  ({email})')

print('\nDone!')
print('Login hub: http://127.0.0.1:8000/accounts/login/')
print('  Student example: cs001 / student123')
print('  Parent example:  parent_alice / parent123  (depends on parent_email on record)')
