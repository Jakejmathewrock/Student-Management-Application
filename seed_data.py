"""
Seed all demo data for EduAdmin Pro dashboard.
Run: python seed_data.py
"""
import os, django, random
from decimal import Decimal
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import date, timedelta
from students.models import (
    Student, Department, Course, Teacher, AttendanceRecord,
    Result, Notice, FeeRecord, PaymentTransaction, Assignment, TimetableEntry
)

print("🌱 Seeding data...\n")

# ── Departments ───────────────────────────────────────────────
dept_data = [
    ('Computer Science',       'CS',   'Dr. Alan Turing'),
    ('Mathematics',            'MATH', 'Dr. Emmy Noether'),
    ('Physics',                'PHY',  'Dr. Richard Feynman'),
    ('Business Administration','BBA',  'Dr. Peter Drucker'),
    ('Electrical Engineering', 'EE',   'Dr. Nikola Tesla'),
    ('Civil Engineering',      'CE',   'Dr. Isambard Brunel'),
]
depts = {}
for name, code, head in dept_data:
    d, c = Department.objects.get_or_create(code=code, defaults={'name': name, 'head': head, 'description': f'Department of {name}'})
    depts[code] = d
    if c: print(f"  ✅ Dept: {name}")

# ── Courses ───────────────────────────────────────────────────
course_data = [
    ('Introduction to Programming',    'CS101',  'CS',   3),
    ('Data Structures & Algorithms',   'CS201',  'CS',   4),
    ('Database Systems',               'CS301',  'CS',   3),
    ('Machine Learning',               'CS401',  'CS',   4),
    ('Calculus I',                     'MATH101','MATH', 4),
    ('Linear Algebra',                 'MATH201','MATH', 3),
    ('Mechanics',                      'PHY101', 'PHY',  3),
    ('Business Communication',         'BBA101', 'BBA',  2),
    ('Financial Management',           'BBA201', 'BBA',  3),
    ('Circuit Theory',                 'EE101',  'EE',   4),
]
courses = {}
for name, code, dept_code, credits in course_data:
    c, created = Course.objects.get_or_create(code=code, defaults={'name': name, 'department': depts[dept_code], 'credits': credits})
    courses[code] = c
    if created: print(f"  ✅ Course: {name}")

# ── Teachers ──────────────────────────────────────────────────
teacher_data = [
    ('Prof. Sarah Connor',    'M.Tech, PhD', 8,  'CS',   'Programming, ML, Algorithms',     75000),
    ('Dr. James Watson',      'PhD Physics', 12, 'PHY',  'Mechanics, Thermodynamics',        82000),
    ('Prof. Elena Rodriguez', 'MBA, PhD',    6,  'BBA',  'Finance, Management',              68000),
    ('Dr. Michael Chen',      'M.Sc, PhD',   10, 'MATH', 'Calculus, Linear Algebra',         71000),
    ('Prof. Aisha Patel',     'M.Tech',      4,  'EE',   'Circuit Theory, Electronics',      65000),
    ('Dr. Robert Brown',      'PhD CS',      15, 'CS',   'Database, Software Engineering',   90000),
]
for name, qual, exp, dept_code, subjects, salary in teacher_data:
    t, c = Teacher.objects.get_or_create(name=name, defaults={
        'qualification': qual, 'experience_years': exp,
        'department': depts[dept_code], 'subjects_handling': subjects,
        'salary': Decimal(str(salary))
    })
    if c: print(f"  ✅ Teacher: {name}")

# ── Students ──────────────────────────────────────────────────
students_raw = [
    ('Alice Johnson',   'CS-001', 'alice@edu.com',   'CS',   'CS101',  'female', 3.85, 92.5, 2023),
    ('Bob Smith',       'CS-002', 'bob@edu.com',     'CS',   'CS201',  'male',   3.20, 78.0, 2023),
    ('Carol White',     'MT-001', 'carol@edu.com',   'MATH', 'MATH101','female', 3.60, 88.0, 2022),
    ('David Brown',     'CS-003', 'david@edu.com',   'CS',   'CS301',  'male',   2.90, 65.0, 2023),
    ('Eva Martinez',    'MT-002', 'eva@edu.com',     'MATH', 'MATH201','female', 3.95, 95.0, 2022),
    ('Frank Wilson',    'PH-001', 'frank@edu.com',   'PHY',  'PHY101', 'male',   2.40, 58.0, 2024),
    ('Grace Lee',       'BB-001', 'grace@edu.com',   'BBA',  'BBA101', 'female', 3.10, 82.0, 2023),
    ('Henry Davis',     'EE-001', 'henry@edu.com',   'EE',   'EE101',  'male',   3.50, 90.0, 2022),
    ('Isla Thomas',     'CS-004', 'isla@edu.com',    'CS',   'CS401',  'female', 3.75, 87.0, 2022),
    ('James Anderson',  'MT-003', 'james@edu.com',   'MATH', 'MATH101','male',   2.10, 45.0, 2024),
    ('Karen Taylor',    'BB-002', 'karen@edu.com',   'BBA',  'BBA201', 'female', 3.40, 76.0, 2023),
    ('Leo Jackson',     'EE-002', 'leo@edu.com',     'EE',   'EE101',  'male',   2.80, 70.0, 2023),
    ('Mia Harris',      'CS-005', 'mia@edu.com',     'CS',   'CS101',  'female', 3.65, 93.0, 2024),
    ('Noah Martin',     'PH-002', 'noah@edu.com',    'PHY',  'PHY101', 'male',   3.00, 68.0, 2023),
    ('Olivia Garcia',   'MT-004', 'olivia@edu.com',  'MATH', 'MATH201','female', 3.90, 96.0, 2022),
]
student_objs = []
for full_name, roll, email, dept_code, c_code, gender, gpa, att, year in students_raw:
    s, created = Student.objects.get_or_create(roll_number=roll, defaults={
        'full_name': full_name, 'email': email,
        'department': depts[dept_code], 'course': courses[c_code],
        'gender': gender, 'gpa': Decimal(str(gpa)),
        'attendance_percentage': Decimal(str(att)),
        'status': 'active', 'year_of_admission': year,
        'phone': f'+1-555-{random.randint(1000,9999)}',
        'parent_name': f'{full_name.split()[1]} Sr.',
        'parent_phone': f'+1-555-{random.randint(1000,9999)}',
        'parent_email': f'parent.{roll.lower().replace("-","")}@edu.com',
    })
    student_objs.append(s)
    if created: print(f"  ✅ Student: {full_name}")

# ── Attendance Records ────────────────────────────────────────
statuses = ['present','present','present','present','absent','late','excused']
today = date.today()
added_att = 0
for student in Student.objects.all():
    for i in range(20):
        d = today - timedelta(days=i+1)
        if d.weekday() < 5:  # weekdays only
            status = random.choice(statuses)
            AttendanceRecord.objects.get_or_create(student=student, date=d, defaults={'status': status})
            added_att += 1
    # Recalculate attendance %
    total   = student.attendance_records.count()
    present = student.attendance_records.filter(status__in=['present','late']).count()
    if total > 0:
        student.attendance_percentage = round((present / total) * 100, 2)
        student.save(update_fields=['attendance_percentage'])
print(f"  ✅ Attendance records: {added_att}")

# ── Results ───────────────────────────────────────────────────
grade_map = [(90,'A+'),(80,'A'),(70,'B+'),(60,'B'),(50,'C+'),(40,'C'),(30,'D'),(0,'F')]
def get_grade(pct):
    for threshold, grade in grade_map:
        if pct >= threshold: return grade
    return 'F'

semesters = ['Fall 2023', 'Spring 2024', 'Fall 2024']
added_res = 0
for student in Student.objects.all():
    dept_code = student.department.code if student.department else 'CS'
    dept_courses = list(Course.objects.filter(department=student.department)[:3])
    if not dept_courses:
        dept_courses = list(Course.objects.all()[:2])
    for course in dept_courses:
        sem = random.choice(semesters)
        marks = Decimal(str(round(random.uniform(35, 99), 2)))
        pct = float(marks)
        grade = get_grade(pct)
        r, created = Result.objects.get_or_create(
            student=student, course=course, semester=sem,
            defaults={'marks_obtained': marks, 'total_marks': Decimal('100'), 'grade': grade}
        )
        if created: added_res += 1
print(f"  ✅ Results: {added_res}")

# ── Fee Records ───────────────────────────────────────────────
fee_statuses = ['paid','paid','pending','overdue']
added_fees = 0
for student in Student.objects.all():
    status = random.choice(fee_statuses)
    tuition = Decimal(str(random.choice([25000, 30000, 35000, 40000])))
    exam    = Decimal('2500')
    hostel  = Decimal(str(random.choice([0, 8000, 10000])))
    total   = tuition + exam + hostel
    paid    = total if status == 'paid' else Decimal(str(round(random.uniform(0, float(total)*0.6), 2)))
    due     = today + timedelta(days=random.randint(-30, 60))
    f, c = FeeRecord.objects.get_or_create(student=student, defaults={
        'tuition_fee': tuition, 'exam_fee': exam,
        'hostel_fee': hostel, 'paid_amount': paid,
        'status': status, 'due_date': due,
    })
    if c:
        added_fees += 1
        if status == 'paid':
            PaymentTransaction.objects.create(
                fee_record=f, amount=total,
                transaction_ref=f'TXN-{student.pk:04d}',
                status='completed', paid_by=student.full_name,
            )
print(f"  ✅ Fee records: {added_fees}")

# ── Notices ───────────────────────────────────────────────────
notices = [
    ('Mid-Semester Examination Schedule',    'exam',      'Mid-semester exams will be held from July 15–22, 2026. All students must carry their ID cards. No electronic devices allowed in exam halls. Detailed timetable available on the college portal.'),
    ('Summer Vacation — July 2026',          'holiday',   'The college will remain closed from July 25 to August 5, 2026 for summer vacation. All administrative offices will be closed during this period.'),
    ('Campus Placement Drive — TechCorp',    'placement', 'TechCorp is visiting campus on July 10, 2026 for recruitment. Eligible: CS & EE final-year students with CGPA ≥ 7.0. Register at the placement cell before July 5.'),
    ('Library Late Fee Waiver',              'general',   'The library has announced a one-time late fee waiver for all overdue books. Students must return books by June 30 to avail this offer.'),
    ('Annual Sports Day — Registrations Open','general',  'Annual Sports Day will be held on August 20, 2026. Students can register for athletics, cricket, football, and chess. Last date to register: August 1.'),
    ('Fee Payment Deadline Reminder',        'exam',      'Last date for fee payment without penalty is June 30, 2026. A late fee of ₹500 per week will be charged after the deadline. Pay through the college portal or finance office.'),
]
added_notices = 0
for title, ntype, content in notices:
    n, c = Notice.objects.get_or_create(title=title, defaults={'notice_type': ntype, 'content': content})
    if c: added_notices += 1
print(f"  ✅ Notices: {added_notices}")

# ── Assignments ───────────────────────────────────────────────
assignments = [
    ('Python Calculator Project',   'CS101', 'Build a scientific calculator using Python with GUI.', 10),
    ('Sorting Algorithm Analysis',  'CS201', 'Compare time complexity of 5 sorting algorithms with graphs.', 7),
    ('ER Diagram Design',           'CS301', 'Design an ER diagram for a hospital management system.', 5),
    ('Calculus Problem Set #3',     'MATH101','Solve 20 integration and differentiation problems.', 3),
    ('Financial Statement Analysis','BBA201', 'Analyze the last 3-year financial statements of any listed company.', 8),
]
added_asgn = 0
from students.models import Assignment as Asgn
for title, c_code, desc, days_left in assignments:
    course = courses.get(c_code)
    if not course: continue
    a, c = Asgn.objects.get_or_create(title=title, defaults={
        'course': course, 'description': desc,
        'assigned_date': today - timedelta(days=7),
        'due_date': today + timedelta(days=days_left),
    })
    if c: added_asgn += 1
print(f"  ✅ Assignments: {added_asgn}")

# ── Timetable ─────────────────────────────────────────────────
from datetime import time as dtime
teachers = list(Teacher.objects.all())
timetable_entries = [
    ('Monday',    'CS101',  0, dtime(9,0),  dtime(10,0),  'Lab A'),
    ('Monday',    'MATH101',3, dtime(10,0), dtime(11,0),  'Room 201'),
    ('Tuesday',   'CS201',  0, dtime(9,0),  dtime(10,30), 'Lab B'),
    ('Tuesday',   'BBA101', 2, dtime(11,0), dtime(12,0),  'Room 301'),
    ('Wednesday', 'PHY101', 1, dtime(8,30), dtime(10,0),  'Physics Lab'),
    ('Wednesday', 'CS301',  5, dtime(10,0), dtime(11,0),  'Room 101'),
    ('Thursday',  'EE101',  4, dtime(9,0),  dtime(10,30), 'EE Lab'),
    ('Thursday',  'MATH201',3, dtime(11,0), dtime(12,0),  'Room 202'),
    ('Friday',    'CS401',  0, dtime(9,0),  dtime(10,30), 'Lab C'),
    ('Friday',    'BBA201', 2, dtime(11,0), dtime(12,0),  'Room 302'),
]
added_tt = 0
for day, c_code, t_idx, start, end, venue in timetable_entries:
    course  = courses.get(c_code)
    teacher = teachers[t_idx] if t_idx < len(teachers) else None
    if not course: continue
    tte, c = TimetableEntry.objects.get_or_create(
        day=day, course=course,
        defaults={'teacher': teacher, 'start_time': start, 'end_time': end, 'venue': venue}
    )
    if c: added_tt += 1
print(f"  ✅ Timetable entries: {added_tt}")

print("\n🎉 All data seeded successfully!")
print(f"   Students:    {Student.objects.count()}")
print(f"   Teachers:    {Teacher.objects.count()}")
print(f"   Departments: {Department.objects.count()}")
print(f"   Courses:     {Course.objects.count()}")
print(f"   Attendance:  {AttendanceRecord.objects.count()}")
print(f"   Results:     {Result.objects.count()}")
print(f"   Fee Records: {FeeRecord.objects.count()}")
print(f"   Notices:     {Notice.objects.count()}")
print(f"   Assignments: {Asgn.objects.count()}")
print(f"   Timetable:   {TimetableEntry.objects.count()}")
print("\n👉 Open: http://127.0.0.1:8000  |  admin / admin123")
