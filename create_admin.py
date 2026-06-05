"""
Run this once to create the admin user and sample data.
Usage: python create_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from students.models import Department, Course, Student

# ── Create superuser ──────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@eduadmin.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    UserProfile.objects.get_or_create(user=user, defaults={'role': 'admin'})
    print("✅ Superuser created: username=admin  password=admin123")
else:
    print("ℹ️  Superuser 'admin' already exists.")

# ── Create sample departments ─────────────────────────────────
depts = [
    ('Computer Science', 'CS', 'Dr. Alan Turing'),
    ('Mathematics', 'MATH', 'Dr. Emmy Noether'),
    ('Physics', 'PHY', 'Dr. Richard Feynman'),
    ('Business Administration', 'BBA', 'Dr. Peter Drucker'),
]
for name, code, head in depts:
    dept, created = Department.objects.get_or_create(
        code=code,
        defaults={'name': name, 'head': head, 'description': f'Department of {name}'}
    )
    if created:
        print(f"✅ Department created: {name}")

# ── Create sample courses ─────────────────────────────────────
cs = Department.objects.get(code='CS')
math = Department.objects.get(code='MATH')

courses = [
    ('Introduction to Programming', 'CS101', cs, 3),
    ('Data Structures & Algorithms', 'CS201', cs, 4),
    ('Database Systems', 'CS301', cs, 3),
    ('Calculus I', 'MATH101', math, 4),
    ('Linear Algebra', 'MATH201', math, 3),
]
for name, code, dept, credits in courses:
    course, created = Course.objects.get_or_create(
        code=code,
        defaults={'name': name, 'department': dept, 'credits': credits}
    )
    if created:
        print(f"✅ Course created: {name}")

# ── Create sample students ────────────────────────────────────
import random
from decimal import Decimal

sample_students = [
    ('Alice Johnson', 'CS-001', 'alice@example.com', 'CS', 'CS101', 'female', 3.85, 92.5),
    ('Bob Smith', 'CS-002', 'bob@example.com', 'CS', 'CS201', 'male', 3.20, 78.0),
    ('Carol White', 'MATH-001', 'carol@example.com', 'MATH', 'MATH101', 'female', 3.60, 88.0),
    ('David Brown', 'CS-003', 'david@example.com', 'CS', 'CS301', 'male', 2.90, 65.0),
    ('Eva Martinez', 'MATH-002', 'eva@example.com', 'MATH', 'MATH201', 'female', 3.95, 95.0),
]

for full_name, roll, email, dept_code, course_code, gender, gpa, att in sample_students:
    if not Student.objects.filter(roll_number=roll).exists():
        dept = Department.objects.get(code=dept_code)
        course = Course.objects.get(code=course_code)
        Student.objects.create(
            full_name=full_name,
            roll_number=roll,
            email=email,
            department=dept,
            course=course,
            gender=gender,
            gpa=Decimal(str(gpa)),
            attendance_percentage=Decimal(str(att)),
            status='active',
            year_of_admission=2024,
            phone=f'+1-555-{random.randint(1000,9999)}',
            parent_name=f'{full_name.split()[1]} Sr.',
            parent_phone=f'+1-555-{random.randint(1000,9999)}',
            parent_email=f'parent.{roll.lower().replace("-", "")}@edu.com',
        )
        print(f"✅ Student created: {full_name}")

print("\n🎉 Setup complete! Run: python manage.py runserver")
print("   Then open: http://127.0.0.1:8000/accounts/login/")
print("   Admin:   admin / admin123")
print("   Run:     python create_portal_users.py  (student & parent logins)")
