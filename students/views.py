from django.shortcuts import render, redirect, get_object_or_404
import time
import uuid as uuid_lib
from decimal import Decimal
from datetime import date
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required, student_required, parent_required
from accounts.utils import redirect_url_for_user
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum, F
from django.http import HttpResponse
import csv
import json

from django.contrib.auth.models import User
from .models import (
    Student, Department, Course, AttendanceRecord, Result,
    Notification, Teacher, TimetableEntry, Assignment,
    AssignmentSubmission, Notice, FeeRecord, PaymentTransaction,
    Exam, ExamApplication, FoodItem, FoodOrder, FoodOrderItem,
    Book, BookIssue, HostelRoom, RoomAllocation
)
from .forms import (
    StudentForm, DepartmentForm, CourseForm,
    AttendanceForm, ResultForm, StudentSearchForm,
    TeacherForm, TimetableForm, AssignmentForm,
    SubmissionForm, NoticeForm, FeeRecordForm, PaymentForm,
    ExamForm, ExamApplicationForm, ExamPaymentForm,
    FoodItemForm, FoodCourtPaymentForm,
    BookForm, BookIssueForm,
    HostelRoomForm, RoomAllocationForm,
    LaundryServiceForm,
)


# ─── Dashboard ────────────────────────────────────────────────────────────────

def home(request):
    """Send each role to the right dashboard."""
    if not request.user.is_authenticated:
        return redirect('login')
    target = redirect_url_for_user(request.user)
    if target == 'dashboard':
        return dashboard(request)
    return redirect(target)


@admin_required
def dashboard(request):
    total_students = Student.objects.count()
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()
    total_teachers = Teacher.objects.count()
    active_students = Student.objects.filter(status='active').count()

    avg_gpa = Student.objects.aggregate(avg=Avg('gpa'))['avg'] or 0
    avg_attendance = Student.objects.aggregate(avg=Avg('attendance_percentage'))['avg'] or 0

    recent_students = Student.objects.select_related('department', 'course').order_by('-created_at')[:8]

    # Department-wise student counts for chart
    dept_data = Department.objects.annotate(count=Count('student')).values('name', 'count')
    dept_labels = json.dumps([d['name'] for d in dept_data])
    dept_counts = json.dumps([d['count'] for d in dept_data])

    # GPA distribution
    gpa_excellent = Student.objects.filter(gpa__gte=3.5).count()
    gpa_good = Student.objects.filter(gpa__gte=2.5, gpa__lt=3.5).count()
    gpa_average = Student.objects.filter(gpa__gte=1.5, gpa__lt=2.5).count()
    gpa_poor = Student.objects.filter(gpa__lt=1.5).count()

    # Status distribution
    status_data = Student.objects.values('status').annotate(count=Count('status'))
    notice_count = Notice.objects.count()
    pending_fees = FeeRecord.objects.filter(status__in=['pending', 'overdue']).count()
    latest_notices = Notice.objects.order_by('-created_at')[:3]
    paid_fees = FeeRecord.objects.filter(status='paid').count()
    fee_totals = FeeRecord.objects.aggregate(
        tuition=Sum('tuition_fee'),
        exam=Sum('exam_fee'),
        hostel=Sum('hostel_fee'),
        paid=Sum('paid_amount'),
    )
    fee_expected = (fee_totals['tuition'] or 0) + (fee_totals['exam'] or 0) + (fee_totals['hostel'] or 0)
    fee_collected = fee_totals['paid'] or 0
    fee_due = max(fee_expected - fee_collected, 0)
    fee_collection_rate = round((fee_collected / fee_expected) * 100, 2) if fee_expected else 0

    monthly_student_counts = []
    for month in range(1, 13):
        monthly_student_counts.append(Student.objects.filter(created_at__month=month).count())

    attendance_status = AttendanceRecord.objects.values('status').annotate(count=Count('status'))
    attendance_labels = [item['status'].title() for item in attendance_status]
    attendance_counts = [item['count'] for item in attendance_status]

    performance_labels = [d['name'] for d in dept_data]
    performance_scores = []
    for department in Department.objects.all():
        score = Student.objects.filter(department=department).aggregate(avg=Avg('gpa'))['avg'] or 0
        performance_scores.append(round(float(score), 2))

    recent_activities = [
        {'icon': 'user-plus', 'title': 'New student onboarding', 'meta': f'{recent_students.count() if hasattr(recent_students, "count") else len(recent_students)} recent registrations reviewed'},
        {'icon': 'calendar-check', 'title': 'Attendance audit', 'meta': f'{avg_attendance}% average attendance this semester'},
        {'icon': 'wallet', 'title': 'Fee follow-up queue', 'meta': f'{pending_fees} pending or overdue fee records'},
    ]
    upcoming_events = TimetableEntry.objects.select_related('course', 'teacher').order_by('day', 'start_time')[:4]
    recent_notices = Notice.objects.order_by('-created_at')[:4]
    top_students = Student.objects.select_related('department').order_by('-gpa', '-attendance_percentage')[:5]
    teacher_salary_status = Teacher.objects.select_related('department').order_by('-salary')[:5]

    context = {
        'total_students': total_students,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'total_teachers': total_teachers,
        'active_students': active_students,
        'avg_gpa': round(avg_gpa, 2),
        'avg_attendance': round(avg_attendance, 2),
        'recent_students': recent_students,
        'dept_labels': dept_labels,
        'dept_counts': dept_counts,
        'gpa_excellent': gpa_excellent,
        'gpa_good': gpa_good,
        'gpa_average': gpa_average,
        'gpa_poor': gpa_poor,
        'status_data': status_data,
        'notice_count': notice_count,
        'pending_fees': pending_fees,
        'latest_notices': latest_notices,
        'paid_fees': paid_fees,
        'fee_expected': fee_expected,
        'fee_collected': fee_collected,
        'fee_due': fee_due,
        'fee_collection_rate': fee_collection_rate,
        'student_growth_counts': json.dumps(monthly_student_counts),
        'student_growth_labels': json.dumps(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        'attendance_labels': json.dumps(attendance_labels or ['Present', 'Absent', 'Late', 'Excused']),
        'attendance_counts': json.dumps(attendance_counts or [0, 0, 0, 0]),
        'performance_labels': json.dumps(performance_labels),
        'performance_scores': json.dumps(performance_scores),
        'recent_activities': recent_activities,
        'upcoming_events': upcoming_events,
        'recent_notices': recent_notices,
        'top_students': top_students,
        'teacher_salary_status': teacher_salary_status,
    }
    return render(request, 'dashboard/dashboard.html', context)


# ─── Students ─────────────────────────────────────────────────────────────────

@admin_required
def student_list(request):
    form = StudentSearchForm(request.GET)
    students = Student.objects.select_related('department', 'course').all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        department = form.cleaned_data.get('department')
        status = form.cleaned_data.get('status')
        gender = form.cleaned_data.get('gender')

        if query:
            students = students.filter(
                Q(full_name__icontains=query) |
                Q(roll_number__icontains=query) |
                Q(email__icontains=query) |
                Q(student_id__icontains=query)
            )
        if department:
            students = students.filter(department=department)
        if status:
            students = students.filter(status=status)
        if gender:
            students = students.filter(gender=gender)

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'students/student_list.html', {
        'page_obj': page_obj,
        'form': form,
        'total_count': students.count(),
    })


@admin_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    attendance_records = student.attendance_records.order_by('-date')[:10]
    results = student.results.select_related('course').order_by('-created_at')
    att_present = student.attendance_records.filter(status='present').count()
    att_absent  = student.attendance_records.filter(status='absent').count()
    att_late    = student.attendance_records.filter(status='late').count()
    att_excused = student.attendance_records.filter(status='excused').count()
    return render(request, 'students/student_detail.html', {
        'student': student,
        'attendance_records': attendance_records,
        'results': results,
        'att_present': att_present,
        'att_absent':  att_absent,
        'att_late':    att_late,
        'att_excused': att_excused,
    })


@admin_required
def student_add(request):
    form = StudentForm()
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student "{student.full_name}" added successfully!')
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Add Student'})


@admin_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(instance=student)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student "{student.full_name}" updated successfully!')
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'students/student_form.html', {
        'form': form,
        'title': 'Edit Student',
        'student': student
    })


@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.full_name
        student.delete()
        messages.success(request, f'Student "{name}" deleted successfully.')
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})


@admin_required
def student_export(request):
    students = Student.objects.select_related('department', 'course').all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Full Name', 'Roll Number', 'Email', 'Phone',
        'Gender', 'Department', 'Course', 'GPA', 'Attendance %',
        'Status', 'Year of Admission', 'Parent Name', 'Parent Phone'
    ])
    for s in students:
        writer.writerow([
            s.student_id, s.full_name, s.roll_number, s.email, s.phone,
            s.gender, s.department or '', s.course or '', s.gpa,
            s.attendance_percentage, s.status, s.year_of_admission,
            s.parent_name, s.parent_phone
        ])
    return response


# ─── Departments ──────────────────────────────────────────────────────────────

@admin_required
def department_list(request):
    departments = Department.objects.annotate(student_count=Count('student')).order_by('name')
    return render(request, 'students/department_list.html', {'departments': departments})


@admin_required
def department_add(request):
    form = DepartmentForm()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f'Department "{dept.name}" created!')
            return redirect('department_list')
    return render(request, 'students/department_form.html', {'form': form, 'title': 'Add Department'})


@admin_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(instance=dept)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{dept.name}" updated!')
            return redirect('department_list')
    return render(request, 'students/department_form.html', {'form': form, 'title': 'Edit Department', 'dept': dept})


@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, 'Department deleted.')
        return redirect('department_list')
    return render(request, 'students/department_confirm_delete.html', {'dept': dept})


# ─── Courses ──────────────────────────────────────────────────────────────────

@admin_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(request, 'students/course_list.html', {'courses': courses})


@admin_required
def course_add(request):
    form = CourseForm()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.name}" created!')
            return redirect('course_list')
    return render(request, 'students/course_form.html', {'form': form, 'title': 'Add Course'})


@admin_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(instance=course)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.name}" updated!')
            return redirect('course_list')
    return render(request, 'students/course_form.html', {'form': form, 'title': 'Edit Course', 'course': course})


@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('course_list')
    return render(request, 'students/course_confirm_delete.html', {'course': course})


# ─── Attendance ───────────────────────────────────────────────────────────────

@admin_required
def attendance_list(request):
    records = AttendanceRecord.objects.select_related('student').order_by('-date')
    paginator = Paginator(records, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'students/attendance_list.html', {'page_obj': page_obj})


@admin_required
def attendance_add(request):
    form = AttendanceForm()
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            record = form.save()
            # Recalculate attendance percentage for student
            student = record.student
            total = student.attendance_records.count()
            present = student.attendance_records.filter(status__in=['present', 'late']).count()
            if total > 0:
                student.attendance_percentage = round((present / total) * 100, 2)
                student.save(update_fields=['attendance_percentage'])
                
            # Create Notification
            user = User.objects.filter(email=student.email).first()
            if user:
                Notification.objects.create(user=user, message=f'Your attendance for {record.date} was marked as {record.status}.')
                
            messages.success(request, 'Attendance recorded!')
            return redirect('attendance_list')
    return render(request, 'students/attendance_form.html', {'form': form, 'title': 'Mark Attendance'})


@admin_required
def pending_fees_list(request):
    pending_fees = FeeRecord.objects.filter(status__in=['pending', 'overdue']).select_related('student')
    return render(request, 'students/pending_fees_list.html', {'pending_fees': pending_fees})


@admin_required
def gpa_distribution(request):
    students = Student.objects.select_related('department').all()
    excellent = students.filter(gpa__gte=3.5)
    good      = students.filter(gpa__gte=2.5, gpa__lt=3.5)
    average   = students.filter(gpa__gte=1.5, gpa__lt=2.5)
    poor      = students.filter(gpa__lt=1.5)
    avg_gpa   = students.aggregate(avg=Avg('gpa'))['avg'] or 0

    categories = [
        (excellent, '#22C55E', '🏆 Excellent — GPA ≥ 3.5'),
        (good,      '#3B82F6', '👍 Good — GPA 2.5 to 3.5'),
        (average,   '#F59E0B', '📚 Average — GPA 1.5 to 2.5'),
        (poor,      '#EF4444', '⚠ Needs Attention — GPA < 1.5'),
    ]
    context = {
        'excellent': excellent.count(),
        'good':      good.count(),
        'average':   average.count(),
        'poor':      poor.count(),
        'total':     students.count(),
        'avg_gpa':   avg_gpa,
        'categories': categories,
        'excellent_students': excellent,
        'good_students': good,
        'average_students': average,
        'poor_students': poor,
    }
    return render(request, 'students/gpa_distribution.html', context)


# ─── Results ──────────────────────────────────────────────────────────────────

@admin_required
def result_list(request):
    results = Result.objects.select_related('student', 'course').order_by('-created_at')
    paginator = Paginator(results, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'students/result_list.html', {'page_obj': page_obj})


@admin_required
def result_add(request):
    form = ResultForm()
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save()
            
            # Create Notification
            user = User.objects.filter(email=result.student.email).first()
            if user:
                Notification.objects.create(user=user, message=f'A new result was published for {result.course.name}. Grade: {result.grade}.')
                
            messages.success(request, 'Result added successfully!')
            return redirect('result_list')
    return render(request, 'students/result_form.html', {'form': form, 'title': 'Add Result'})


@admin_required
def result_delete(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Result deleted.')
        return redirect('result_list')
    return render(request, 'students/result_confirm_delete.html', {'result': result})


# ─── Teacher Module ───────────────────────────────────────────────────────────

@admin_required
def teacher_list(request):
    teachers = Teacher.objects.select_related('department').all()
    return render(request, 'students/teacher_list.html', {'teachers': teachers})


@admin_required
def teacher_add(request):
    form = TeacherForm()
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher added successfully!')
            return redirect('teacher_list')
    return render(request, 'students/teacher_form.html', {'form': form, 'title': 'Add Teacher'})


@admin_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(instance=teacher)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher updated successfully!')
            return redirect('teacher_list')
    return render(request, 'students/teacher_form.html', {'form': form, 'title': 'Edit Teacher', 'teacher': teacher})


@admin_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Teacher deleted.')
        return redirect('teacher_list')
    return render(request, 'students/teacher_confirm_delete.html', {'teacher': teacher})


# ─── Timetable Module ─────────────────────────────────────────────────────────

@admin_required
def timetable_list(request):
    schedule = TimetableEntry.objects.select_related('course', 'teacher').all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return render(request, 'students/timetable_list.html', {
        'schedule': schedule,
        'days': days,
    })


@admin_required
def timetable_add(request):
    form = TimetableForm()
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry created.')
            return redirect('timetable_list')
    return render(request, 'students/timetable_form.html', {'form': form, 'title': 'Add Timetable Entry'})


@admin_required
def timetable_edit(request, pk):
    entry = get_object_or_404(TimetableEntry, pk=pk)
    form = TimetableForm(instance=entry)
    if request.method == 'POST':
        form = TimetableForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry updated.')
            return redirect('timetable_list')
    return render(request, 'students/timetable_form.html', {'form': form, 'title': 'Edit Timetable Entry', 'entry': entry})


@admin_required
def timetable_delete(request, pk):
    entry = get_object_or_404(TimetableEntry, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Timetable entry deleted.')
        return redirect('timetable_list')
    return render(request, 'students/timetable_confirm_delete.html', {'entry': entry})


# ─── Assignments ──────────────────────────────────────────────────────────────

@admin_required
def assignment_list(request):
    assignments = Assignment.objects.select_related('course').all()
    submissions = AssignmentSubmission.objects.select_related('assignment', 'student').all()
    return render(request, 'students/assignment_list.html', {'assignments': assignments, 'submissions': submissions})


@admin_required
def assignment_add(request):
    form = AssignmentForm()
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('assignment_list')
    return render(request, 'students/assignment_form.html', {'form': form, 'title': 'Create Assignment'})


@admin_required
def assignment_submit(request):
    form = SubmissionForm()
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignment_list')
    return render(request, 'students/assignment_submit.html', {'form': form, 'title': 'Submit Assignment'})


# ─── Notice Board ────────────────────────────────────────────────────────────

@admin_required
def notice_list(request):
    notices = Notice.objects.all()
    return render(request, 'students/notice_list.html', {'notices': notices})


@admin_required
def notice_add(request):
    form = NoticeForm()
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice posted successfully!')
            return redirect('notice_list')
    return render(request, 'students/notice_form.html', {'form': form, 'title': 'Post Notice'})


# ─── Fees ─────────────────────────────────────────────────────────────────────

@admin_required
def fee_list(request):
    fees = FeeRecord.objects.select_related('student').all()
    from django.db.models import Sum
    totals = fees.aggregate(
        tuition=Sum('tuition_fee'), exam=Sum('exam_fee'),
        hostel=Sum('hostel_fee'),  paid=Sum('paid_amount')
    )
    fee_expected   = (totals['tuition'] or 0) + (totals['exam'] or 0) + (totals['hostel'] or 0)
    fee_collected  = totals['paid'] or 0
    fee_due        = max(fee_expected - fee_collected, 0)
    collection_rate = round((fee_collected / fee_expected) * 100, 1) if fee_expected else 0
    paid_count    = fees.filter(status='paid').count()
    pending_count = fees.filter(status='pending').count()
    overdue_count = fees.filter(status='overdue').count()
    return render(request, 'students/fee_list.html', {
        'fees':            fees,
        'fee_expected':    fee_expected,
        'fee_collected':   fee_collected,
        'fee_due':         fee_due,
        'collection_rate': collection_rate,
        'total_records':   fees.count(),
        'paid_count':      paid_count,
        'pending_count':   pending_count,
        'overdue_count':   overdue_count,
    })


@admin_required
def fee_add(request):
    form = FeeRecordForm()
    if request.method == 'POST':
        form = FeeRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee record saved successfully!')
            return redirect('fee_list')
    return render(request, 'students/fee_form.html', {'form': form, 'title': 'Add Fee Record'})


@login_required
def fee_payment(request, pk):
    fee = get_object_or_404(FeeRecord, pk=pk)
    due_amount = fee.total_due()
    if due_amount <= 0:
        messages.warning(request, 'This fee record is already fully paid.')
        return redirect('fee_list')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            upi_id = form.cleaned_data['upi_id']
            if amount > due_amount:
                form.add_error('amount', 'Amount cannot exceed the outstanding due.')
            else:
                fee.paid_amount += amount
                if fee.total_due() <= 0:
                    fee.status = 'paid'
                elif fee.due_date and fee.due_date < date.today():
                    fee.status = 'overdue'
                else:
                    fee.status = 'pending'
                fee.save(update_fields=['paid_amount', 'status'])

                PaymentTransaction.objects.create(
                    fee_record=fee,
                    amount=amount,
                    upi_id=upi_id,
                    transaction_ref=f'UPI-{fee.pk}-{int(time.time())}',
                    status='completed',
                    paid_by=request.user.get_full_name() or request.user.username,
                )
                messages.success(request, 'Payment completed successfully via UPI.')
                return redirect('fee_list')
    else:
        form = PaymentForm(initial={'amount': due_amount, 'upi_id': 'eduadmin@upi'})

    return render(request, 'students/fee_payment.html', {
        'form': form,
        'fee': fee,
        'due_amount': due_amount,
        'upi_account': 'eduadmin@upi',
    })


# ─── Export utilities ──────────────────────────────────────────────────────────

@admin_required
def attendance_export(request):
    records = AttendanceRecord.objects.select_related('student').order_by('-date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_records.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student', 'Date', 'Status', 'Remarks'])
    for rec in records:
        writer.writerow([rec.student.full_name, rec.date, rec.status, rec.remarks])
    return response


@admin_required
def result_export(request):
    results = Result.objects.select_related('student', 'course').order_by('-created_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="results.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student', 'Course', 'Semester', 'Marks Obtained', 'Total Marks', 'Grade', 'Remarks'])
    for res in results:
        writer.writerow([
            res.student.full_name, res.course.name, res.semester,
            res.marks_obtained, res.total_marks, res.grade, res.remarks
        ])
    return response


@admin_required
def student_export_excel(request):
    students = Student.objects.select_related('department', 'course').all()
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="students.xls"'
    writer = csv.writer(response, delimiter='\t')
    writer.writerow([
        'Student ID', 'Full Name', 'Roll Number', 'Email', 'Phone',
        'Department', 'Course', 'GPA', 'Attendance %', 'Status'
    ])
    for s in students:
        writer.writerow([
            s.student_id, s.full_name, s.roll_number, s.email, s.phone,
            s.department or '', s.course or '', s.gpa,
            s.attendance_percentage, s.status
        ])
    return response


@admin_required
def student_export_pdf(request):
    students = Student.objects.select_related('department', 'course').all()
    return render(request, 'students/student_export_pdf.html', {'students': students})


# ─── Student ID Card ───────────────────────────────────────────────────────────

@admin_required
def student_id_card(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_id_card.html', {'student': student})


# ─── Student / Parent Portal ──────────────────────────────────────────────────

def _children_for_parent(user):
    email = (user.email or '').strip()
    if not email:
        return Student.objects.none()
    return Student.objects.filter(
        parent_email__iexact=email
    ).select_related('department', 'course')


@parent_required
def parent_dashboard(request):
    children = _children_for_parent(request.user)
    children_data = []
    for child in children:
        fees = child.fees.all()
        pending = sum(
            max(f.total_due(), 0) for f in fees if f.status != 'paid'
        )
        children_data.append({
            'student': child,
            'pending_fees': pending,
            'results_count': child.results.count(),
            'exam_apps': child.exam_applications.count(),
            'attendance': child.attendance_percentage,
        })
    return render(request, 'dashboard/parent_dashboard.html', {
        'children': children,
        'children_data': children_data,
    })


@parent_required
def parent_child_detail(request, pk):
    child = get_object_or_404(
        Student.objects.select_related('department', 'course'), pk=pk
    )
    parent_email = (request.user.email or '').strip()
    if not parent_email or child.parent_email.lower() != parent_email.lower():
        raise PermissionDenied

    fees = child.fees.all().order_by('-created_at')
    results = child.results.select_related('course').order_by('-created_at')
    attendance = child.attendance_records.order_by('-date')[:10]
    exam_apps = child.exam_applications.select_related('exam').order_by('-applied_at')

    return render(request, 'dashboard/parent_child_detail.html', {
        'child': child,
        'fees': fees,
        'results': results,
        'attendance': attendance,
        'exam_apps': exam_apps,
    })


@student_required
def student_dashboard(request):
    try:
        student = Student.objects.get(email=request.user.email)
        attendance_records = student.attendance_records.order_by('-date')[:5]
        results = student.results.select_related('course').order_by('-created_at')
        laundry_orders = student.laundry_orders.order_by('-ordered_at')[:4]

        context = {
            'student':           student,
            'attendance_records':attendance_records,
            'results':           results,
            'laundry_orders':    laundry_orders,
            'laundry_services':  LaundryService.objects.filter(is_available=True).order_by('category','name'),
        }
    except Student.DoesNotExist:
        context = {
            'error': 'Your student profile has not been linked yet. Please contact the administration.'
        }
    return render(request, 'dashboard/student_dashboard.html', context)


# ═══════════════════════════════════════════════════════════════
#  EXAM MODULE VIEWS
# ═══════════════════════════════════════════════════════════════

# ─── Admin: Exam CRUD ─────────────────────────────────────────

@admin_required
def exam_list(request):
    """All exams with fee totals."""
    exams = Exam.objects.select_related('course', 'department').order_by('-exam_date')
    from django.db.models import Sum, Count
    for exam in exams:
        exam.applicant_count = exam.applications.count()
        exam.approved_count  = exam.applications.filter(status='approved').count()
        exam.fee_total       = exam.applications.filter(
            payment_status='paid'
        ).aggregate(s=Sum('fee_paid'))['s'] or 0
    return render(request, 'exams/exam_list.html', {'exams': exams})


@admin_required
def exam_create(request):
    form = ExamForm()
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f'Exam "{exam.title}" created successfully!')
            return redirect('exam_list')
    return render(request, 'exams/exam_form.html', {'form': form, 'title': 'Create Exam'})


@admin_required
def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    form = ExamForm(instance=exam)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f'Exam "{exam.title}" updated!')
            return redirect('exam_list')
    return render(request, 'exams/exam_form.html', {'form': form, 'title': 'Edit Exam', 'exam': exam})


@admin_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted.')
        return redirect('exam_list')
    return render(request, 'exams/exam_confirm_delete.html', {'exam': exam})


@admin_required
def exam_detail(request, pk):
    """Admin view — all applications for this exam with fee summary."""
    exam        = get_object_or_404(Exam, pk=pk)
    applications = exam.applications.select_related('student').order_by('-applied_at')
    from django.db.models import Sum, Count
    fee_collected = applications.filter(payment_status='paid').aggregate(
        s=Sum('fee_paid')
    )['s'] or 0
    fee_expected  = exam.exam_fee * applications.filter(
        payment_status='paid'
    ).count()
    stats = {
        'total':     applications.count(),
        'pending':   applications.filter(status='pending').count(),
        'approved':  applications.filter(status='approved').count(),
        'rejected':  applications.filter(status='rejected').count(),
        'paid':      applications.filter(payment_status='paid').count(),
        'unpaid':    applications.filter(payment_status='unpaid').count(),
        'fee_collected': fee_collected,
        'seats_left': exam.seats_available(),
    }
    return render(request, 'exams/exam_detail.html', {
        'exam': exam,
        'applications': applications,
        'stats': stats,
    })


@admin_required
def application_approve(request, pk):
    app = get_object_or_404(ExamApplication, pk=pk)
    app.status = 'approved'
    app.save()
    messages.success(request, f'{app.student.full_name} approved. Hall ticket: {app.hall_ticket_no}')
    return redirect('exam_detail', pk=app.exam.pk)


@admin_required
def application_reject(request, pk):
    app = get_object_or_404(ExamApplication, pk=pk)
    app.status = 'rejected'
    app.save()
    messages.warning(request, f'{app.student.full_name}\'s application rejected.')
    return redirect('exam_detail', pk=app.exam.pk)


# ─── Student: Apply for Exam ──────────────────────────────────

@login_required
def exam_portal(request):
    """All open exams visible to students / admin."""
    if hasattr(request.user, 'profile') and request.user.profile.role == 'parent':
        messages.info(request, 'View your child\'s exam applications from the parent dashboard.')
        return redirect('parent_dashboard')

    from datetime import date
    today = date.today()
    open_exams = Exam.objects.filter(
        status='open', apply_start__lte=today, apply_end__gte=today
    ).select_related('course', 'department').order_by('exam_date')
    upcoming_exams = Exam.objects.filter(status='upcoming').order_by('exam_date')[:4]
    my_applications = []
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(email=request.user.email)
            my_applications = ExamApplication.objects.filter(
                student=student
            ).select_related('exam').order_by('-applied_at')
        except Student.DoesNotExist:
            pass
    applied_exam_ids = {app.exam_id for app in my_applications}
    return render(request, 'exams/exam_portal.html', {
        'open_exams': open_exams,
        'upcoming_exams': upcoming_exams,
        'my_applications': my_applications,
        'applied_exam_ids': applied_exam_ids,
    })


@login_required
def exam_apply(request, pk):
    """Student applies for an exam — shows fee, collects UPI."""
    if hasattr(request.user, 'profile') and request.user.profile.role != 'student':
        if request.user.profile.role == 'parent':
            messages.error(request, 'Only students can apply for exams.')
            return redirect('parent_dashboard')
        messages.error(request, 'Only students can apply for exams.')
        return redirect('exam_portal')

    exam = get_object_or_404(Exam, pk=pk)

    # Find the student profile
    try:
        student = Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        messages.error(request, 'Your student profile is not linked. Contact admin.')
        return redirect('exam_portal')

    # Already applied?
    existing = ExamApplication.objects.filter(exam=exam, student=student).first()
    if existing:
        messages.info(request, 'You have already applied for this exam.')
        return redirect('exam_application_status', pk=existing.pk)

    # Check if open
    from datetime import date
    today = date.today()
    if not (exam.apply_start <= today <= exam.apply_end and exam.status == 'open'):
        messages.error(request, 'Applications for this exam are not open.')
        return redirect('exam_portal')

    # Seats check
    if exam.seats_available() <= 0:
        messages.error(request, 'No seats available for this exam.')
        return redirect('exam_portal')

    form = ExamPaymentForm()
    if request.method == 'POST':
        form = ExamPaymentForm(request.POST)
        if form.is_valid():
            upi_id = form.cleaned_data['upi_id']
            import uuid as _uuid
            txn_id = f'EXAM-{exam.pk}-{str(_uuid.uuid4()).upper()[:8]}'

            app = ExamApplication.objects.create(
                exam=exam,
                student=student,
                status='pending',
                payment_status='paid' if exam.fee_required else 'waived',
                fee_paid=exam.exam_fee if exam.fee_required else 0,
                upi_id=upi_id,
                transaction_id=txn_id,
                paid_at=timezone.now() if exam.fee_required else None,
                remarks=f'Applied online via EduAdmin Pro. UPI: {upi_id}',
            )
            messages.success(request,
                f'Application submitted! Transaction ID: {txn_id}. '
                f'Fee of ₹{exam.exam_fee} paid successfully.'
            )
            return redirect('exam_application_status', pk=app.pk)

    return render(request, 'exams/exam_apply.html', {
        'exam': exam,
        'student': student,
        'form': form,
        'upi_account': 'eduadmin@upi',
    })


@login_required
def exam_application_status(request, pk):
    """Student sees their application status + hall ticket."""
    app = get_object_or_404(ExamApplication, pk=pk)
    return render(request, 'exams/exam_application_status.html', {'app': app})


@login_required
def hall_ticket(request, pk):
    """Printable hall ticket for approved applications."""
    app = get_object_or_404(ExamApplication, pk=pk, status='approved')
    return render(request, 'exams/hall_ticket.html', {'app': app})


# ═══════════════════════════════════════════════════════════════
#  FOOD COURT
# ═══════════════════════════════════════════════════════════════

def _student_for_request(request):
    try:
        return Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        return None


def _food_cart_get(request):
    return request.session.get('food_cart', {})


def _food_cart_set(request, cart):
    request.session['food_cart'] = cart
    request.session.modified = True


def _food_cart_lines(request):
    cart = _food_cart_get(request)
    lines = []
    total = Decimal('0')
    for item_id, qty in cart.items():
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            continue
        if qty < 1:
            continue
        food = FoodItem.objects.filter(pk=int(item_id), is_available=True).first()
        if not food:
            continue
        sub = food.price * qty
        lines.append({'food': food, 'qty': qty, 'subtotal': sub})
        total += sub
    return lines, total


@student_required
def food_court(request):
    """Browse menu and add items to cart."""
    student = _student_for_request(request)
    if not student:
        messages.error(request, 'Your student profile is not linked. Contact admin.')
        return redirect('student_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        cart = _food_cart_get(request)

        if action == 'add' and item_id:
            food = get_object_or_404(FoodItem, pk=item_id, is_available=True)
            cart[str(food.pk)] = cart.get(str(food.pk), 0) + 1
            _food_cart_set(request, cart)
            messages.success(request, f'Added {food.name} to cart.')
        elif action == 'remove' and item_id:
            cart.pop(str(item_id), None)
            _food_cart_set(request, cart)
        elif action == 'update_qty' and item_id:
            qty = int(request.POST.get('quantity', 1))
            if qty <= 0:
                cart.pop(str(item_id), None)
            else:
                cart[str(item_id)] = qty
            _food_cart_set(request, cart)

        return redirect('food_court')

    items = FoodItem.objects.filter(is_available=True)
    by_category = {}
    for item in items:
        by_category.setdefault(item.get_category_display(), []).append(item)

    lines, cart_total = _food_cart_lines(request)
    cart_count = sum(l['qty'] for l in lines)

    return render(request, 'food/food_court.html', {
        'by_category': by_category,
        'cart_lines': lines,
        'cart_total': cart_total,
        'cart_count': cart_count,
        'student': student,
    })


@student_required
def food_checkout(request):
    """Pay for cart via UPI."""
    student = _student_for_request(request)
    if not student:
        messages.error(request, 'Your student profile is not linked.')
        return redirect('student_dashboard')

    lines, total = _food_cart_lines(request)
    if not lines:
        messages.warning(request, 'Your cart is empty. Add food items first.')
        return redirect('food_court')

    form = FoodCourtPaymentForm()
    if request.method == 'POST':
        form = FoodCourtPaymentForm(request.POST)
        if form.is_valid():
            upi_id = form.cleaned_data['upi_id']
            txn_id = f'FOOD-{str(uuid_lib.uuid4()).upper()[:10]}'

            order = FoodOrder.objects.create(
                student=student,
                total_amount=total,
                payment_status='paid',
                order_status='pending',
                upi_id=upi_id,
                transaction_id=txn_id,
                paid_at=timezone.now(),
            )
            for line in lines:
                FoodOrderItem.objects.create(
                    order=order,
                    food_item=line['food'],
                    quantity=line['qty'],
                    unit_price=line['food'].price,
                    subtotal=line['subtotal'],
                )

            _food_cart_set(request, {})
            messages.success(
                request,
                f'Order placed! Paid ₹{total}. Transaction: {txn_id}'
            )
            return redirect('food_order_detail', pk=order.pk)

    return render(request, 'food/food_checkout.html', {
        'student': student,
        'cart_lines': lines,
        'cart_total': total,
        'form': form,
        'upi_account': 'eduadmin@upi',
    })


@student_required
def food_order_detail(request, pk):
    order = get_object_or_404(
        FoodOrder.objects.prefetch_related('items__food_item'),
        pk=pk,
        student__email=request.user.email,
    )
    return render(request, 'food/food_order_detail.html', {'order': order})


@student_required
def food_my_orders(request):
    student = _student_for_request(request)
    orders = FoodOrder.objects.filter(student=student).prefetch_related('items') if student else []
    return render(request, 'food/food_my_orders.html', {
        'orders': orders,
        'student': student,
    })


@admin_required
def food_menu_admin(request):
    items = FoodItem.objects.all()
    return render(request, 'food/food_menu_admin.html', {'items': items})


@admin_required
def food_item_add(request):
    form = FoodItemForm()
    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food item added.')
            return redirect('food_menu_admin')
    return render(request, 'food/food_item_form.html', {'form': form, 'title': 'Add Food Item'})


@admin_required
def food_item_edit(request, pk):
    item = get_object_or_404(FoodItem, pk=pk)
    form = FoodItemForm(instance=item)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food item updated.')
            return redirect('food_menu_admin')
    return render(request, 'food/food_item_form.html', {'form': form, 'title': 'Edit Food Item'})


@admin_required
def food_orders_admin(request):
    orders = FoodOrder.objects.select_related('student').prefetch_related('items__food_item').order_by('-ordered_at')
    
    query = request.GET.get('query', '').strip()
    status = request.GET.get('status', '').strip()
    payment = request.GET.get('payment', '').strip()
    
    if query:
        try:
            order_id = int(query)
            orders = orders.filter(
                Q(pk=order_id) |
                Q(student__full_name__icontains=query) |
                Q(student__roll_number__icontains=query)
            )
        except ValueError:
            orders = orders.filter(
                Q(student__full_name__icontains=query) |
                Q(student__roll_number__icontains=query)
            )
            
    if status:
        orders = orders.filter(order_status=status)
    if payment:
        orders = orders.filter(payment_status=payment)
        
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('order_status')
        order = get_object_or_404(FoodOrder, pk=order_id)
        if new_status in dict(FoodOrder.STATUS_CHOICES):
            order.order_status = new_status
            order.save()
            messages.success(request, f'Order #{order.pk} marked as {order.get_order_status_display()}.')
        return redirect('food_orders_admin')
        
    context = {
        'orders': orders,
        'query': query,
        'selected_status': status,
        'selected_payment': payment,
        'status_choices': FoodOrder.STATUS_CHOICES,
        'payment_choices': FoodOrder.PAYMENT_CHOICES,
    }
    return render(request, 'food/food_orders_admin.html', context)



# ═══════════════════════════════════════════════════════════════
#  LIBRARY MODULE VIEWS
# ═══════════════════════════════════════════════════════════════

# ─── Admin: Book CRUD ─────────────────────────────────────────

@admin_required
def book_list(request):
    """View and manage all books in the library."""
    query = request.GET.get('query', '').strip()
    category = request.GET.get('category', '').strip()
    
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    if category:
        books = books.filter(category__icontains=category)
        
    # Get distinct categories for the filter dropdown
    categories = Book.objects.values_list('category', flat=True).distinct()
    
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'library/book_list.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_category': category,
        'categories': categories,
        'total_count': books.count(),
    })


@admin_required
def book_add(request):
    """Add a new book to the library."""
    form = BookForm()
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.available_copies = book.total_copies
            book.save()
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('book_list')
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Add Book'})


@admin_required
def book_edit(request, pk):
    """Edit book details."""
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(instance=book)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            edited_book = form.save(commit=False)
            active_issues = BookIssue.objects.filter(book=book, status='issued').count()
            edited_book.available_copies = max(edited_book.total_copies - active_issues, 0)
            edited_book.save()
            messages.success(request, f'Book "{edited_book.title}" updated successfully!')
            return redirect('book_list')
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Edit Book', 'book': book})


@admin_required
def book_delete(request, pk):
    """Delete a book from library if no active issues exist."""
    book = get_object_or_404(Book, pk=pk)
    active_issues = BookIssue.objects.filter(book=book, status='issued').count()
    
    if active_issues > 0:
        messages.error(request, f'Cannot delete "{book.title}" because it has {active_issues} active checkouts.')
        return redirect('book_list')
        
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" was deleted.')
        return redirect('book_list')
        
    return render(request, 'library/book_confirm_delete.html', {'book': book})


# ─── Admin: Book Issue & Returns ─────────────────────────────

@admin_required
def issue_list(request):
    """List all issues, showing fine details and stats."""
    status_filter = request.GET.get('status', '').strip()
    issues = BookIssue.objects.select_related('book', 'student').all()
    
    if status_filter:
        issues = issues.filter(status=status_filter)
        
    # Update overdue status in real time for list rendering
    from datetime import date
    today = date.today()
    for issue in issues:
        if issue.status == 'issued' and today > issue.due_date:
            issue.status = 'overdue'
            issue.save(update_fields=['status'])

    # Calculate statistics
    total_books = Book.objects.aggregate(Sum('total_copies'))['total_copies__sum'] or 0
    total_issued = BookIssue.objects.filter(status__in=['issued', 'overdue']).count()
    overdue_issues = BookIssue.objects.filter(status='overdue').count()
    
    # Calculate fines
    fines_collected = BookIssue.objects.filter(fine_paid=True).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0
    
    # Calculate pending fines
    pending_fines = 0
    all_active_issues = BookIssue.objects.filter(status__in=['issued', 'overdue'])
    for issue in all_active_issues:
        pending_fines += issue.current_fine()
    # Add returned but unpaid fines
    pending_fines += BookIssue.objects.filter(status='returned', fine_paid=False).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0

    paginator = Paginator(issues, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    stats = {
        'total_books': total_books,
        'total_issued': total_issued,
        'overdue_count': overdue_issues,
        'fines_collected': fines_collected,
        'fines_pending': pending_fines,
    }

    return render(request, 'library/issue_list.html', {
        'page_obj': page_obj,
        'selected_status': status_filter,
        'stats': stats,
    })


@admin_required
def issue_add(request):
    """Issue a book to a student."""
    from datetime import date, timedelta
    initial_data = {
        'issue_date': date.today(),
        'due_date': date.today() + timedelta(days=14)
    }
    form = BookIssueForm(initial=initial_data)
    
    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            book = issue.book
            
            # Check availability
            if book.available_copies <= 0:
                form.add_error('book', 'No copies of this book are currently available.')
            else:
                book.available_copies -= 1
                book.save()
                
                if date.today() > issue.due_date:
                    issue.status = 'overdue'
                else:
                    issue.status = 'issued'
                    
                issue.save()
                
                # Notify Student
                user = User.objects.filter(email=issue.student.email).first()
                if user:
                    Notification.objects.create(
                        user=user, 
                        message=f'Book "{book.title}" has been issued to you. Due date is {issue.due_date}.'
                    )
                    
                messages.success(request, f'Book "{book.title}" successfully issued to {issue.student.full_name}.')
                return redirect('issue_list')
                
    return render(request, 'library/issue_form.html', {'form': form, 'title': 'Issue Book'})


@admin_required
def issue_return(request, pk):
    """Process return of a book and calculate fine."""
    issue = get_object_or_404(BookIssue, pk=pk)
    
    if issue.status == 'returned' or issue.return_date:
        messages.warning(request, 'This book has already been returned.')
        return redirect('issue_list')
        
    from datetime import date
    today = date.today()
    
    fine = issue.current_fine()
    
    issue.return_date = today
    issue.status = 'returned'
    issue.fine_amount = fine
    if fine == 0:
        issue.fine_paid = True
    issue.save()
    
    book = issue.book
    book.available_copies = min(book.available_copies + 1, book.total_copies)
    book.save()
    
    user = User.objects.filter(email=issue.student.email).first()
    if user:
        msg = f'Book "{book.title}" has been returned.'
        if fine > 0:
            msg += f' Fine of ₹{fine} calculated.'
        Notification.objects.create(user=user, message=msg)
        
    if fine > 0:
        messages.warning(request, f'Book returned. Fine of ₹{fine} incurred.')
    else:
        messages.success(request, 'Book returned successfully!')
        
    return redirect('issue_list')


@admin_required
def settle_fine(request, pk):
    """Mark outstanding fine as paid."""
    issue = get_object_or_404(BookIssue, pk=pk)
    if issue.fine_amount > 0 or not issue.fine_paid:
        if issue.fine_amount == 0:
            # If dynamic fine hadn't been saved yet, compute it
            issue.fine_amount = issue.current_fine()
        issue.fine_paid = True
        issue.save()
        messages.success(request, f'Fine of ₹{issue.fine_amount} for "{issue.book.title}" marked as settled.')
    else:
        messages.info(request, 'No outstanding fine to settle.')
    return redirect('issue_list')


# ─── Student: Library Portal ──────────────────────────────────

@login_required
def library_portal(request):
    """Student portal view to browse books and view checkout history."""
    if hasattr(request.user, 'profile') and request.user.profile.role == 'parent':
        messages.info(request, "Library portal is currently viewable by students directly.")
        return redirect('parent_dashboard')

    try:
        student = Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        messages.error(request, 'Your student profile is not linked. Contact admin.')
        return redirect('home')

    query = request.GET.get('query', '').strip()
    category = request.GET.get('category', '').strip()
    
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    if category:
        books = books.filter(category__icontains=category)
        
    categories = Book.objects.values_list('category', flat=True).distinct()
    
    my_issues = BookIssue.objects.filter(student=student).select_related('book').order_by('-issue_date')
    
    outstanding_fine = 0
    for issue in my_issues:
        if not issue.fine_paid:
            outstanding_fine += issue.current_fine()

    paginator = Paginator(books, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'library/library_portal.html', {
        'student': student,
        'page_obj': page_obj,
        'query': query,
        'selected_category': category,
        'categories': categories,
        'my_issues': my_issues,
        'outstanding_fine': outstanding_fine,
    })


@student_required
def student_timetable(request):
    """Student portal view to check weekly timetable schedule and subject details."""
    try:
        student = Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        messages.error(request, 'Your student profile is not linked. Contact admin.')
        return redirect('home')

    # Query all timetable entries matching student's department or specific course
    schedule = TimetableEntry.objects.filter(
        Q(course=student.course) | Q(course__department=student.department)
    ).select_related('course', 'teacher').distinct().order_by('start_time')

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    # Group timetable entries by day in python to make rendering simple
    schedule_by_day = {day: [] for day in days}
    for entry in schedule:
        if entry.day in schedule_by_day:
            schedule_by_day[entry.day].append(entry)

    return render(request, 'students/student_timetable.html', {
        'student': student,
        'schedule_by_day': schedule_by_day,
        'days': days,
        'has_entries': len(schedule) > 0,
    })


# ═══════════════════════════════════════════════════════════════
#  HOSTEL MANAGEMENT VIEWS
# ═══════════════════════════════════════════════════════════════

# ─── Admin: Rooms CRUD ────────────────────────────────────────

@admin_required
def room_list(request):
    """List and search all hostel rooms."""
    query = request.GET.get('query', '').strip()
    room_type = request.GET.get('room_type', '').strip()

    rooms = HostelRoom.objects.all()
    if query:
        rooms = rooms.filter(room_number__icontains=query)
    if room_type:
        rooms = rooms.filter(room_type=room_type)

    paginator = Paginator(rooms, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hostel/room_list.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_type': room_type,
        'total_count': rooms.count(),
        'room_types': HostelRoom.ROOM_TYPE_CHOICES,
    })


@admin_required
def room_add(request):
    """Add a new room to the hostel."""
    form = HostelRoomForm()
    if request.method == 'POST':
        form = HostelRoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Hostel Room "{room.room_number}" added successfully!')
            return redirect('room_list')
    return render(request, 'hostel/room_form.html', {'form': form, 'title': 'Add Hostel Room'})


@admin_required
def room_edit(request, pk):
    """Edit room details."""
    room = get_object_or_404(HostelRoom, pk=pk)
    form = HostelRoomForm(instance=room)
    if request.method == 'POST':
        form = HostelRoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hostel Room "{room.room_number}" updated successfully!')
            return redirect('room_list')
    return render(request, 'hostel/room_form.html', {'form': form, 'title': 'Edit Hostel Room', 'room': room})


@admin_required
def room_delete(request, pk):
    """Delete a room if no students are currently allocated."""
    room = get_object_or_404(HostelRoom, pk=pk)
    if room.current_occupancy > 0:
        messages.error(request, f'Cannot delete Room "{room.room_number}" because students are currently allocated to it.')
        return redirect('room_list')

    if request.method == 'POST':
        num = room.room_number
        room.delete()
        messages.success(request, f'Hostel Room "{num}" was deleted.')
        return redirect('room_list')
    return render(request, 'hostel/room_confirm_delete.html', {'room': room})


# ─── Admin: Room Allocations ─────────────────────────────────

@admin_required
def allocation_list(request):
    """View active and past room allocations."""
    status_filter = request.GET.get('status', 'active').strip()
    allocations = RoomAllocation.objects.select_related('room', 'student').all()

    if status_filter:
        allocations = allocations.filter(status=status_filter)

    paginator = Paginator(allocations, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hostel/allocation_list.html', {
        'page_obj': page_obj,
        'selected_status': status_filter,
    })


@admin_required
def allocation_add(request):
    """Allocate a hostel room to a student and update hostel fees."""
    form = RoomAllocationForm()
    if request.method == 'POST':
        form = RoomAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            room = allocation.room
            student = allocation.student

            # Enforce capacity
            if room.current_occupancy >= room.capacity:
                form.add_error('room', 'This room has reached its maximum occupancy.')
            else:
                allocation.status = 'active'
                allocation.save()

                # Update room occupancy
                room.current_occupancy += 1
                room.save()

                # Update or create FeeRecord to add hostel fee
                from datetime import date, timedelta
                fee_record = FeeRecord.objects.filter(
                    student=student,
                    status__in=['pending', 'overdue']
                ).order_by('-created_at').first()

                if fee_record:
                    fee_record.hostel_fee = room.fee_per_semester
                    # Recompute status if needed
                    fee_record.save()
                else:
                    # Create a new FeeRecord
                    FeeRecord.objects.create(
                        student=student,
                        hostel_fee=room.fee_per_semester,
                        status='pending',
                        due_date=date.today() + timedelta(days=30)
                    )

                # Notify student
                user = User.objects.filter(email=student.email).first()
                if user:
                    Notification.objects.create(
                        user=user,
                        message=f'You have been allocated Hostel Room {room.room_number}. Hostel fee of ₹{room.fee_per_semester} added to your profile.'
                    )

                messages.success(request, f'Allocated Room {room.room_number} to {student.full_name} successfully.')
                return redirect('allocation_list')

    return render(request, 'hostel/allocation_form.html', {'form': form, 'title': 'Allocate Room'})


@admin_required
def allocation_checkout(request, pk):
    """Check a student out of their room allocation."""
    allocation = get_object_or_404(RoomAllocation, pk=pk, status='active')
    room = allocation.room
    student = allocation.student

    if request.method == 'POST':
        from datetime import date
        # Update allocation details
        allocation.status = 'checked_out'
        allocation.checkout_date = date.today()
        allocation.save()

        # Update room occupancy
        room.current_occupancy = max(room.current_occupancy - 1, 0)
        room.save()

        # Notify student
        user = User.objects.filter(email=student.email).first()
        if user:
            Notification.objects.create(
                user=user,
                message=f'You have been checked out from Hostel Room {room.room_number}.'
            )

        messages.success(request, f'Checked out {student.full_name} from Room {room.room_number} successfully.')
        return redirect('allocation_list')

    return render(request, 'hostel/allocation_confirm_checkout.html', {
        'allocation': allocation
    })


# ─── Student: Hostel Portal ──────────────────────────────────

@login_required
def hostel_portal(request):
    """Portal view for students — room details, rules, booking request, laundry."""
    if hasattr(request.user, 'profile') and request.user.profile.role == 'parent':
        messages.info(request, 'View hostel room status from student dashboards.')
        return redirect('parent_dashboard')

    try:
        student = Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        messages.error(request, 'Your student profile is not linked. Contact admin.')
        return redirect('home')

    # Current active room allocation
    allocation = RoomAllocation.objects.filter(
        student=student, status='active'
    ).select_related('room').first()

    roommates      = []
    hostel_fees_due = 0
    hostel_fee_status = 'N/A'

    if allocation:
        roommates = RoomAllocation.objects.filter(
            room=allocation.room, status='active'
        ).exclude(student=student).select_related('student')

        latest_fee = FeeRecord.objects.filter(student=student).order_by('-created_at').first()
        if latest_fee:
            hostel_fees_due    = latest_fee.hostel_fee - latest_fee.paid_amount if latest_fee.status != 'paid' else 0
            hostel_fee_status  = latest_fee.get_status_display()

    # Handle room booking/change request
    booking_success = False
    if request.method == 'POST' and request.POST.get('action') == 'room_request':
        room_type_pref = request.POST.get('room_type_pref', '')
        block_pref     = request.POST.get('block_pref', '')
        reason         = request.POST.get('reason', '')
        Notification.send(
            user       = request.user,
            message    = f'Room request submitted by {student.full_name}. Type: {room_type_pref}, Block: {block_pref}. Reason: {reason}',
            notif_type = 'announcement',
            title      = 'Hostel Room Request',
            priority   = 'high',
        )
        messages.success(request, '✅ Room request submitted! The hostel office will contact you within 2 working days.')
        booking_success = True

    # All available rooms for booking request
    available_rooms = HostelRoom.objects.filter(
        current_occupancy__lt=F('capacity')
    ).order_by('room_number') if not allocation else []

    # Laundry services grouped by category
    from itertools import groupby
    all_svcs = LaundryService.objects.filter(is_available=True).order_by('category', 'name')
    laundry_grouped = {}
    cat_meta = {
        'washing':  ('👕', 'Washing Clothes'),
        'drying':   ('☀️', 'Drying Clothes'),
        'ironing':  ('🔥', 'Ironing'),
        'folding':  ('📦', 'Folding Clothes'),
        'bedding':  ('🛏️', 'Bed Sheets & Pillow Covers'),
        'towels':   ('🪣', 'Towels & Cleaning'),
        'special':  ('✨', 'Special Care'),
    }
    for svc in all_svcs:
        cat = svc.category
        if cat not in laundry_grouped:
            laundry_grouped[cat] = {'meta': cat_meta.get(cat, ('🧺', cat.title())), 'items': []}
        laundry_grouped[cat]['items'].append(svc)

    # Recent laundry orders
    recent_laundry_orders = student.laundry_orders.order_by('-ordered_at')[:3]

    return render(request, 'hostel/hostel_portal.html', {
        'student':               student,
        'allocation':            allocation,
        'roommates':             roommates,
        'hostel_fee_due':        hostel_fees_due,
        'hostel_fee_status':     hostel_fee_status,
        'available_rooms':       available_rooms,
        'booking_success':       booking_success,
        'laundry_grouped':       laundry_grouped,
        'recent_laundry_orders': recent_laundry_orders,
    })





# ═══════════════════════════════════════════════════════════════
#  NOTIFICATION CENTER VIEWS
# ═══════════════════════════════════════════════════════════════

@login_required
def notification_list(request):
    """Full notifications page — all notifications for this user."""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Filter by type
    ftype = request.GET.get('type', '')
    if ftype:
        notifs = notifs.filter(notif_type=ftype)

    # Filter by read status
    fread = request.GET.get('read', '')
    if fread == '0':
        notifs = notifs.filter(is_read=False)
    elif fread == '1':
        notifs = notifs.filter(is_read=True)

    # Mark all as read if requested
    if request.GET.get('mark_all') == '1':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notification_list')

    total   = Notification.objects.filter(user=request.user).count()
    unread  = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'notifications/notification_list.html', {
        'notifs':      notifs,
        'total':       total,
        'unread':      unread,
        'ftype':       ftype,
        'fread':       fread,
        'type_choices': Notification.TYPE_CHOICES,
    })


@login_required
def notification_mark_read(request, pk):
    """Mark a single notification as read and redirect to its link."""
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    if notif.link:
        return redirect(notif.link)
    return redirect('notification_list')


@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read (AJAX or direct)."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'status': 'ok'})
    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')


@login_required
def notification_delete(request, pk):
    """Delete a single notification."""
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('notification_list')


@admin_required
def notification_send(request):
    """Admin: send a notification to one or all users."""
    from django.contrib.auth.models import User as AuthUser
    if request.method == 'POST':
        target   = request.POST.get('target', 'all')
        ntype    = request.POST.get('notif_type', 'announcement')
        title    = request.POST.get('title', '')
        message  = request.POST.get('message', '')
        priority = request.POST.get('priority', 'medium')
        link     = request.POST.get('link', '')

        if not message.strip():
            messages.error(request, 'Message cannot be empty.')
        else:
            if target == 'all':
                users = AuthUser.objects.filter(is_active=True)
                Notification.broadcast(users, message, ntype, title, link, priority)
                messages.success(request, f'Notification sent to {users.count()} users.')
            else:
                try:
                    user = AuthUser.objects.get(pk=int(target))
                    Notification.send(user, message, ntype, title, link, priority)
                    messages.success(request, f'Notification sent to {user.username}.')
                except (AuthUser.DoesNotExist, ValueError):
                    messages.error(request, 'User not found.')
            return redirect('notification_send')

    users = AuthUser.objects.filter(is_active=True).order_by('username')
    return render(request, 'notifications/notification_send.html', {
        'users':        users,
        'type_choices': Notification.TYPE_CHOICES,
    })


# ═══════════════════════════════════════════════════════════════
#  LAUNDRY MODULE VIEWS
# ═══════════════════════════════════════════════════════════════

from .models import LaundryService, LaundryOrder, LaundryOrderItem

@login_required
def laundry_portal(request):
    """Student laundry portal — browse services grouped by category."""
    from itertools import groupby
    all_services = LaundryService.objects.filter(is_available=True).order_by('category', 'name')

    # Group by category
    grouped = {}
    for svc in all_services:
        cat_label = svc.get_category_display()
        if cat_label not in grouped:
            grouped[cat_label] = []
        grouped[cat_label].append(svc)

    # Student's past orders
    my_orders = []
    try:
        student = Student.objects.get(email=request.user.email)
        my_orders = LaundryOrder.objects.filter(student=student).order_by('-ordered_at')[:5]
    except Student.DoesNotExist:
        student = None

    return render(request, 'laundry/laundry_portal.html', {
        'grouped':    grouped,
        'my_orders':  my_orders,
        'student':    student,
    })


@login_required
def laundry_place_order(request):
    """Place a laundry order — add items with quantities, then pay."""
    try:
        student = Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        # Admin/staff can still access the page with first student for demo
        if request.user.is_staff:
            student = Student.objects.first()
            if not student:
                messages.error(request, 'No student profiles exist yet.')
                return redirect('laundry_portal')
        else:
            messages.error(request, 'Your student profile is not linked. Contact admin.')
            return redirect('laundry_portal')

    services = LaundryService.objects.filter(is_available=True).order_by('category', 'name')

    if request.method == 'POST':
        upi_id    = request.POST.get('upi_id', '').strip()
        room_no   = request.POST.get('room_number', '').strip()
        pickup_dt = request.POST.get('pickup_date', '')
        notes     = request.POST.get('special_instructions', '')

        # Collect quantities
        items_data = []
        total = 0
        for svc in services:
            qty_str = request.POST.get(f'qty_{svc.pk}', '0')
            try:
                qty = int(qty_str)
            except ValueError:
                qty = 0
            if qty > 0:
                sub = svc.price_per_item * qty
                items_data.append({'service': svc, 'qty': qty, 'unit_price': svc.price_per_item, 'sub': sub})
                total += sub

        if not items_data:
            messages.error(request, 'Please select at least one service.')
            return render(request, 'laundry/laundry_place_order.html', {'services': services, 'student': student})

        if not upi_id:
            messages.error(request, 'Please enter your UPI ID to complete payment.')
            return render(request, 'laundry/laundry_place_order.html', {'services': services, 'student': student})

        import uuid as _uuid
        txn_id = f"LDY-TXN-{str(_uuid.uuid4()).upper()[:10]}"

        order = LaundryOrder.objects.create(
            student        = student,
            status         = 'placed',
            payment_status = 'paid',
            total_amount   = total,
            paid_amount    = total,
            upi_id         = upi_id,
            transaction_id = txn_id,
            paid_at        = timezone.now(),
            room_number    = room_no,
            pickup_date    = pickup_dt or None,
            special_instructions = notes,
        )

        for item in items_data:
            LaundryOrderItem.objects.create(
                order      = order,
                service    = item['service'],
                quantity   = item['qty'],
                unit_price = item['unit_price'],
                subtotal   = item['sub'],
            )

        # Send notification
        Notification.send(
            user       = request.user,
            message    = f'Laundry order #{order.order_number} placed! ₹{total:.0f} paid. Pickup scheduled.',
            notif_type = 'announcement',
            title      = 'Laundry Order Confirmed',
            link       = f'/laundry/order/{order.pk}/',
            priority   = 'medium',
        )

        messages.success(request, f'Order #{order.order_number} placed! ₹{total:.0f} paid via UPI. TXN: {txn_id}')
        return redirect('laundry_order_detail', pk=order.pk)

    return render(request, 'laundry/laundry_place_order.html', {
        'services': services,
        'student':  student,
    })


@login_required
def laundry_order_detail(request, pk):
    """Student: view a single order detail."""
    try:
        student = Student.objects.get(email=request.user.email)
        order   = get_object_or_404(LaundryOrder, pk=pk, student=student)
    except Student.DoesNotExist:
        order = get_object_or_404(LaundryOrder, pk=pk)
    return render(request, 'laundry/laundry_order_detail.html', {'order': order})


@login_required
def laundry_my_orders(request):
    """Student: all their laundry orders."""
    try:
        student   = Student.objects.get(email=request.user.email)
        orders    = LaundryOrder.objects.filter(student=student).order_by('-ordered_at')
    except Student.DoesNotExist:
        # Admin/staff can still access the page with first student for demo
        if request.user.is_staff:
            student = Student.objects.first()
            if student:
                orders = LaundryOrder.objects.filter(student=student).order_by('-ordered_at')
            else:
                orders = LaundryOrder.objects.none()
                student = None
        else:
            orders  = LaundryOrder.objects.none()
            student = None
    return render(request, 'laundry/laundry_my_orders.html', {'orders': orders, 'student': student})


# ── Admin laundry views ──────────────────────────────────────

@admin_required
def laundry_admin_orders(request):
    """Admin: all laundry orders with filters."""
    orders = LaundryOrder.objects.select_related('student').order_by('-ordered_at')
    
    query = request.GET.get('query', '').strip()
    status_filter = request.GET.get('status', '').strip()
    payment_filter = request.GET.get('payment', '').strip()
    
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(student__full_name__icontains=query) |
            Q(student__roll_number__icontains=query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)
    if payment_filter:
        orders = orders.filter(payment_status=payment_filter)

    if request.method == 'POST':
        order_id  = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        if order_id and new_status:
            ord_obj = get_object_or_404(LaundryOrder, pk=order_id)
            ord_obj.status = new_status
            ord_obj.save(update_fields=['status'])
            # Notify student
            try:
                user = User.objects.get(email=ord_obj.student.email)
                status_msg = dict(LaundryOrder.STATUS_CHOICES).get(new_status, new_status)
                Notification.send(
                    user       = user,
                    message    = f'Your laundry order #{ord_obj.order_number} status: {status_msg}',
                    notif_type = 'announcement',
                    title      = f'Laundry Update: {status_msg}',
                    link       = f'/laundry/order/{ord_obj.pk}/',
                )
            except User.DoesNotExist:
                pass
            messages.success(request, f'Order #{ord_obj.order_number} updated to {new_status}.')
            return redirect('laundry_admin_orders')

    from django.db.models import Sum
    all_orders = LaundryOrder.objects.all()
    summary = {
        'total':     all_orders.count(),
        'placed':    all_orders.filter(status='placed').count(),
        'processing':all_orders.filter(status='processing').count(),
        'ready':     all_orders.filter(status='ready').count(),
        'delivered': all_orders.filter(status='delivered').count(),
        'revenue':   all_orders.filter(payment_status='paid').aggregate(t=Sum('paid_amount'))['t'] or 0,
    }
    return render(request, 'laundry/laundry_admin_orders.html', {
        'orders':        orders,
        'summary':       summary,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'query':         query,
        'status_choices': LaundryOrder.STATUS_CHOICES,
        'payment_choices': LaundryOrder.PAYMENT_CHOICES,
    })


@admin_required
def laundry_services_admin(request):
    """Admin: manage laundry service prices."""
    services = LaundryService.objects.all().order_by('category', 'name')
    return render(request, 'laundry/laundry_services_admin.html', {'services': services})


@admin_required
def laundry_service_toggle(request, pk):
    """Admin: toggle service availability."""
    svc = get_object_or_404(LaundryService, pk=pk)
    svc.is_available = not svc.is_available
    svc.save(update_fields=['is_available'])
    messages.success(request, f'{"Enabled" if svc.is_available else "Disabled"}: {svc.name}')
    return redirect('laundry_services_admin')


# ═══════════════════════════════════════════════════════════════
#  PAYMENT MANAGEMENT SYSTEM
# ═══════════════════════════════════════════════════════════════

import hmac, hashlib, io, base64
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

def _get_razorpay_client():
    import razorpay
    return razorpay.Client(auth=(
        getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_demo'),
        getattr(settings, 'RAZORPAY_KEY_SECRET', 'demo_secret'),
    ))

def _generate_upi_qr(upi_id, name, amount, note='Fee Payment'):
    """Generate base64-encoded QR code image for UPI payment."""
    import qrcode
    upi_str = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR&tn={note}"
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(upi_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()


# ─── Student Payment Dashboard ────────────────────────────────

@login_required
def payment_dashboard(request):
    """Student sees all their fee records and payment history."""
    try:
        student = Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        if request.user.is_staff:
            student = Student.objects.first()
        else:
            messages.error(request, 'Student profile not linked.')
            return redirect('home')

    fee_records = FeeRecord.objects.filter(student=student).order_by('-created_at')
    transactions = PaymentTransaction.objects.filter(
        fee_record__student=student
    ).select_related('fee_record').order_by('-created_at')

    total_fees  = sum(f.tuition_fee + f.exam_fee + f.hostel_fee for f in fee_records)
    total_paid  = sum(f.paid_amount for f in fee_records)
    total_due   = max(total_fees - total_paid, 0)
    paid_count  = fee_records.filter(status='paid').count()
    pending_count = fee_records.filter(status__in=['pending','overdue']).count()

    return render(request, 'payments/dashboard.html', {
        'student':       student,
        'fee_records':   fee_records,
        'transactions':  transactions[:10],
        'total_fees':    total_fees,
        'total_paid':    total_paid,
        'total_due':     total_due,
        'paid_count':    paid_count,
        'pending_count': pending_count,
    })


# ─── Initiate Payment (UPI + Razorpay) ────────────────────────

@login_required
def payment_initiate(request, fee_pk):
    """Show payment page with UPI QR and Razorpay option."""
    fee = get_object_or_404(FeeRecord, pk=fee_pk)
    due = fee.total_due()

    if due <= 0:
        messages.info(request, 'This fee is already fully paid.')
        return redirect('payment_dashboard')

    # Generate UPI QR code
    upi_id   = getattr(settings, 'UPI_ID', 'eduadmin@upi')
    upi_name = getattr(settings, 'UPI_NAME', 'EduAdmin College')
    qr_b64   = _generate_upi_qr(upi_id, upi_name, float(due),
                                  f'Fee-{fee.student.roll_number}')

    # Create Razorpay order
    rz_order = None
    rz_key   = getattr(settings, 'RAZORPAY_KEY_ID', '')
    try:
        client   = _get_razorpay_client()
        rz_order = client.order.create({
            'amount':   int(due * 100),  # paise
            'currency': 'INR',
            'receipt':  f'fee_{fee.pk}',
            'notes':    {'student': fee.student.full_name, 'fee_id': str(fee.pk)},
        })
    except Exception:
        rz_order = None  # Razorpay not configured — fall back to UPI

    return render(request, 'payments/initiate.html', {
        'fee':       fee,
        'due':       due,
        'qr_b64':    qr_b64,
        'upi_id':    upi_id,
        'upi_name':  upi_name,
        'rz_order':  rz_order,
        'rz_key':    rz_key,
    })


# ─── UPI Payment (manual confirmation) ────────────────────────

@login_required
def payment_upi_confirm(request, fee_pk):
    """Student confirms UPI payment by entering transaction ID."""
    fee = get_object_or_404(FeeRecord, pk=fee_pk)
    due = fee.total_due()

    if request.method == 'POST':
        upi_ref  = request.POST.get('upi_ref', '').strip()
        upi_id   = request.POST.get('upi_id', '').strip()
        amount   = due

        if not upi_ref:
            messages.error(request, 'Please enter the UPI transaction reference number.')
            return redirect('payment_initiate', fee_pk=fee_pk)

        txn = PaymentTransaction.objects.create(
            fee_record      = fee,
            amount          = amount,
            method          = 'upi',
            upi_id          = upi_id,
            transaction_ref = upi_ref,
            status          = 'pending',  # pending admin approval
            paid_by         = request.user.get_full_name() or request.user.username,
            notes           = f'UPI payment submitted. Ref: {upi_ref}',
        )

        # Send notification to admin
        from django.contrib.auth.models import User as AuthUser
        admins = AuthUser.objects.filter(is_staff=True)
        Notification.broadcast(
            admins,
            f'{fee.student.full_name} submitted UPI payment of ₹{amount} (Ref: {upi_ref})',
            'fee_due', 'Payment Approval Required',
            f'/payments/admin/approve/{txn.pk}/', 'high'
        )
        # Notify student
        Notification.send(
            request.user,
            f'Payment of ₹{amount} submitted for review. Ref: {upi_ref}',
            'fee_paid', 'Payment Submitted',
            f'/payments/history/', 'medium'
        )

        messages.success(request, f'Payment submitted for approval. Ref: {upi_ref}')
        return redirect('payment_pending', txn_pk=txn.pk)

    return redirect('payment_initiate', fee_pk=fee_pk)


# ─── Razorpay Callback ─────────────────────────────────────────

@csrf_exempt
def payment_razorpay_callback(request):
    """Razorpay payment success callback — verify signature."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    rp_order_id   = request.POST.get('razorpay_order_id', '')
    rp_payment_id = request.POST.get('razorpay_payment_id', '')
    rp_signature  = request.POST.get('razorpay_signature', '')
    fee_pk        = request.POST.get('fee_pk', '')

    # Verify signature
    secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '').encode()
    payload = f"{rp_order_id}|{rp_payment_id}".encode()
    expected_sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()

    fee = get_object_or_404(FeeRecord, pk=fee_pk)

    if hmac.compare_digest(expected_sig, rp_signature):
        # Payment verified
        txn = PaymentTransaction.objects.create(
            fee_record           = fee,
            amount               = fee.total_due(),
            method               = 'razorpay',
            razorpay_order_id    = rp_order_id,
            razorpay_payment_id  = rp_payment_id,
            razorpay_signature   = rp_signature,
            status               = 'completed',
            paid_at              = timezone.now(),
            paid_by              = request.user.get_full_name() or request.user.username,
        )
        _mark_fee_paid(fee, txn.amount)
        messages.success(request, f'Payment successful! Razorpay ID: {rp_payment_id}')
        return redirect('payment_success', txn_pk=txn.pk)
    else:
        txn = PaymentTransaction.objects.create(
            fee_record          = fee,
            amount              = fee.total_due(),
            method              = 'razorpay',
            razorpay_order_id   = rp_order_id,
            razorpay_payment_id = rp_payment_id,
            status              = 'failed',
            notes               = 'Signature verification failed',
        )
        return redirect('payment_failure', txn_pk=txn.pk)


def _mark_fee_paid(fee, amount):
    """Update fee record after successful payment."""
    fee.paid_amount += amount
    if fee.total_due() <= 0:
        fee.status = 'paid'
    fee.save(update_fields=['paid_amount', 'status'])


# ─── Payment Status Pages ──────────────────────────────────────

@login_required
def payment_success(request, txn_pk):
    txn = get_object_or_404(PaymentTransaction, pk=txn_pk)
    return render(request, 'payments/success.html', {'txn': txn})


@login_required
def payment_failure(request, txn_pk):
    txn = get_object_or_404(PaymentTransaction, pk=txn_pk)
    return render(request, 'payments/failure.html', {'txn': txn})


@login_required
def payment_pending(request, txn_pk):
    txn = get_object_or_404(PaymentTransaction, pk=txn_pk)
    return render(request, 'payments/pending.html', {'txn': txn})


# ─── Payment History ──────────────────────────────────────────

@login_required
def payment_history(request):
    """All transactions for the logged-in student."""
    try:
        student = Student.objects.get(email=request.user.email)
        txns = PaymentTransaction.objects.filter(
            fee_record__student=student
        ).select_related('fee_record').order_by('-created_at')
    except Student.DoesNotExist:
        txns = PaymentTransaction.objects.none()
        student = None
    return render(request, 'payments/history.html', {'txns': txns, 'student': student})


# ─── Receipt PDF Download ─────────────────────────────────────

@login_required
def payment_receipt_pdf(request, txn_pk):
    """Generate and download a PDF receipt."""
    txn = get_object_or_404(PaymentTransaction, pk=txn_pk, status='completed')
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph(
        "<font size=20><b>EduAdmin University</b></font>",
        ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)
    ))
    elements.append(Paragraph(
        "<font size=11 color='#2563EB'>Official Fee Payment Receipt</font>",
        ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB')))
    elements.append(Spacer(1, 0.4*cm))

    # Receipt details
    fee = txn.fee_record
    data = [
        ['Receipt No.',   txn.receipt_number or '—',    'Date', txn.paid_at.strftime('%d %b %Y') if txn.paid_at else '—'],
        ['Student Name',  fee.student.full_name,         'Roll No.', fee.student.roll_number],
        ['Department',    str(fee.student.department or '—'), 'Course', str(fee.student.course or '—')],
        ['Payment Method',txn.get_method_display(),      'Transaction Ref', txn.transaction_ref or txn.razorpay_payment_id or '—'],
    ]
    t = Table(data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#EFF6FF')),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('FONTNAME',   (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',   (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING',    (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*cm))

    # Fee breakdown
    elements.append(Paragraph("<b>Fee Breakdown</b>", styles['Heading3']))
    fee_data = [
        ['Description', 'Amount (₹)'],
        ['Tuition Fee', f"{fee.tuition_fee:.2f}"],
        ['Exam Fee',    f"{fee.exam_fee:.2f}"],
        ['Hostel Fee',  f"{fee.hostel_fee:.2f}"],
        ['Amount Paid', f"{txn.amount:.2f}"],
        ['Balance Due', f"{fee.total_due():.2f}"],
    ]
    ft = Table(fee_data, colWidths=[12*cm, 5*cm])
    ft.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0),  colors.HexColor('#2563EB')),
        ('TEXTCOLOR',   (0,0), (-1,0),  colors.white),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTNAME',    (0,1), (-1,-2), 'Helvetica'),
        ('FONTNAME',    (0,-2),(-1,-1), 'Helvetica-Bold'),
        ('ALIGN',       (1,0), (1,-1),  'RIGHT'),
        ('GRID',        (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND',  (0,-2),(-1,-1), colors.HexColor('#F0FDF4')),
        ('TEXTCOLOR',   (0,-2),(-1,-2), colors.HexColor('#15803D')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING',     (0,0), (-1,-1), 7),
    ]))
    elements.append(ft)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0')))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(
        "<font size=8 color='#64748B'>This is a computer-generated receipt and does not require a signature. "
        "For queries contact: fees@eduadmin.edu | +91-1800-000-0000</font>",
        ParagraphStyle('footer', alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{txn.receipt_number or txn.pk}.pdf"'
    return response


# ─── Admin Payment Management ─────────────────────────────────

@admin_required
def payment_admin_list(request):
    """Admin: all transactions with stats."""
    from django.db.models import Sum, Count
    txns = PaymentTransaction.objects.select_related(
        'fee_record__student', 'approved_by'
    ).order_by('-created_at')

    status_filter = request.GET.get('status', '')
    if status_filter:
        txns = txns.filter(status=status_filter)

    stats = {
        'total':     PaymentTransaction.objects.count(),
        'pending':   PaymentTransaction.objects.filter(status='pending').count(),
        'completed': PaymentTransaction.objects.filter(status='completed').count(),
        'failed':    PaymentTransaction.objects.filter(status='failed').count(),
        'revenue':   PaymentTransaction.objects.filter(status='completed').aggregate(
                         t=Sum('amount'))['t'] or 0,
    }
    return render(request, 'payments/admin_list.html', {
        'txns':          txns,
        'stats':         stats,
        'status_filter': status_filter,
    })


@admin_required
def payment_admin_approve(request, txn_pk):
    """Admin approves a pending UPI payment."""
    txn = get_object_or_404(PaymentTransaction, pk=txn_pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            txn.status      = 'completed'
            txn.approved_by = request.user
            txn.approved_at = timezone.now()
            txn.paid_at     = timezone.now()
            txn.save()
            _mark_fee_paid(txn.fee_record, txn.amount)
            # Notify student
            try:
                user = User.objects.get(email=txn.fee_record.student.email)
                Notification.send(user,
                    f'Your payment of ₹{txn.amount} has been approved. Receipt: {txn.receipt_number}',
                    'fee_paid', 'Payment Approved ✅', '/payments/history/', 'high')
            except User.DoesNotExist:
                pass
            messages.success(request, f'Payment ₹{txn.amount} approved.')
        elif action == 'reject':
            txn.status = 'failed'
            txn.notes  = request.POST.get('reject_reason', 'Rejected by admin')
            txn.save()
            messages.warning(request, 'Payment rejected.')
        return redirect('payment_admin_list')

    return render(request, 'payments/admin_approve.html', {'txn': txn})


# ═══════════════════════════════════════════════════════════════
#  MISSING CRUD + EXPORT VIEWS  (Phase 1 completions)
# ═══════════════════════════════════════════════════════════════

# ── Food Court: Delete item ───────────────────────────────────

@admin_required
def food_item_delete(request, pk):
    item = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f'Food item "{name}" deleted.')
        return redirect('food_menu_admin')
    return render(request, 'food/food_item_confirm_delete.html', {'item': item})


# ── Food Court: Export CSV ────────────────────────────────────

@admin_required
def food_orders_export(request):
    orders = FoodOrder.objects.select_related('student').prefetch_related('items__food_item').order_by('-ordered_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="food_orders.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order #', 'Student', 'Roll No', 'Items', 'Total (₹)', 'Payment', 'Status', 'Ordered At'])
    for order in orders:
        items_str = '; '.join(f"{i.food_item.name} x{i.quantity}" for i in order.items.all())
        writer.writerow([
            order.pk, order.student.full_name, order.student.roll_number,
            items_str, order.total_amount,
            order.get_payment_status_display(), order.get_order_status_display(),
            order.ordered_at.strftime('%d %b %Y %H:%M'),
        ])
    return response


# ── Laundry: Service Add / Edit / Delete ─────────────────────

@admin_required
def laundry_service_add(request):
    form = LaundryServiceForm()
    if request.method == 'POST':
        form = LaundryServiceForm(request.POST)
        if form.is_valid():
            svc = form.save()
            messages.success(request, f'Service "{svc.name}" added.')
            return redirect('laundry_services_admin')
    return render(request, 'laundry/laundry_service_form.html', {'form': form, 'title': 'Add Laundry Service'})


@admin_required
def laundry_service_edit(request, pk):
    svc = get_object_or_404(LaundryService, pk=pk)
    form = LaundryServiceForm(instance=svc)
    if request.method == 'POST':
        form = LaundryServiceForm(request.POST, instance=svc)
        if form.is_valid():
            form.save()
            messages.success(request, f'Service "{svc.name}" updated.')
            return redirect('laundry_services_admin')
    return render(request, 'laundry/laundry_service_form.html', {'form': form, 'title': 'Edit Laundry Service', 'svc': svc})


@admin_required
def laundry_service_delete(request, pk):
    svc = get_object_or_404(LaundryService, pk=pk)
    if request.method == 'POST':
        name = svc.name
        svc.delete()
        messages.success(request, f'Service "{name}" deleted.')
        return redirect('laundry_services_admin')
    return render(request, 'laundry/laundry_service_confirm_delete.html', {'svc': svc})


# ── Laundry: Export CSV ───────────────────────────────────────

@admin_required
def laundry_orders_export(request):
    orders = LaundryOrder.objects.select_related('student').prefetch_related('items__service').order_by('-ordered_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="laundry_orders.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order #', 'Student', 'Roll No', 'Services', 'Total (₹)', 'Payment', 'Status', 'Ordered At'])
    for order in orders:
        items_str = '; '.join(f"{i.service.name} x{i.quantity}" for i in order.items.all())
        writer.writerow([
            order.order_number, order.student.full_name, order.student.roll_number,
            items_str, order.total_amount,
            order.get_payment_status_display(), order.get_status_display(),
            order.ordered_at.strftime('%d %b %Y %H:%M'),
        ])
    return response


# ── Transport: Export CSV ─────────────────────────────────────

@admin_required
def transport_fee_export(request):
    from transport.models import TransportFee
    fees = TransportFee.objects.select_related('student', 'route').order_by('-created_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transport_fees.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student', 'Roll No', 'Route', 'Fee (₹)', 'Discount (₹)', 'Paid (₹)', 'Status', 'Due Date'])
    for fee in fees:
        writer.writerow([
            fee.student.full_name, fee.student.roll_number,
            str(fee.route) if fee.route else '—',
            fee.fee_amount, fee.discount, fee.paid_amount,
            fee.get_status_display(),
            fee.due_date.strftime('%d %b %Y') if fee.due_date else '—',
        ])
    return response


# ── Exam: confirm-delete template (was missing) ───────────────
# (view already exists — exam_delete — template was the gap, handled in templates)


# ── Exam: Export CSV ──────────────────────────────────────────

@admin_required
def exam_export(request):
    from django.db.models import Sum
    exams = Exam.objects.select_related('course', 'department').order_by('-exam_date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exams.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Type', 'Course', 'Department', 'Date', 'Venue', 'Total Seats', 'Applicants', 'Approved', 'Fee Collected (₹)', 'Status'])
    for exam in exams:
        approved = exam.applications.filter(status='approved').count()
        fee_col  = exam.applications.filter(payment_status='paid').aggregate(s=Sum('fee_paid'))['s'] or 0
        writer.writerow([
            exam.title, exam.get_exam_type_display(),
            str(exam.course or '—'), str(exam.department or '—'),
            exam.exam_date.strftime('%d %b %Y'),
            exam.venue or '—', exam.total_seats,
            exam.applications.count(), approved, fee_col,
            exam.get_status_display(),
        ])
    return response


# ── Payment: Export CSV ───────────────────────────────────────

@admin_required
def payment_export(request):
    txns = PaymentTransaction.objects.select_related('fee_record__student').order_by('-created_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payment_transactions.csv"'
    writer = csv.writer(response)
    writer.writerow(['Receipt #', 'Student', 'Roll No', 'Amount (₹)', 'Method', 'Status', 'Paid At', 'Transaction Ref'])
    for txn in txns:
        writer.writerow([
            txn.receipt_number or '—',
            txn.fee_record.student.full_name,
            txn.fee_record.student.roll_number,
            txn.amount,
            txn.get_method_display(),
            txn.get_status_display(),
            txn.paid_at.strftime('%d %b %Y %H:%M') if txn.paid_at else '—',
            txn.transaction_ref or txn.razorpay_payment_id or '—',
        ])
    return response


# ─── PDF Exports & Utilities (Phase 1 & 2) ───────────────────

def _verify_student_or_admin(request, student):
    if request.user.is_staff:
        return True
    try:
        req_student = Student.objects.get(email=request.user.email)
        return req_student == student
    except Student.DoesNotExist:
        return False


@login_required
def food_order_invoice_pdf(request, pk):
    order = get_object_or_404(FoodOrder, pk=pk)
    if not _verify_student_or_admin(request, order.student):
        raise PermissionDenied
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

    # Title / Header
    elements.append(Paragraph("<font size=20><b>EduAdmin Campus Food Court</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=11 color='#10B981'>Order Invoice / Bill Receipt</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#10B981')))
    elements.append(Spacer(1, 0.4*cm))

    # Details Table
    details = [
        ['Order ID', f'#{order.pk}', 'Date', order.ordered_at.strftime('%d %b %Y %H:%M')],
        ['Student Name', order.student.full_name, 'Roll Number', order.student.roll_number],
        ['Payment Status', order.get_payment_status_display(), 'Order Status', order.get_order_status_display()],
        ['Transaction ID', order.transaction_id or '—', 'UPI ID', order.upi_id or '—'],
    ]
    dt = Table(details, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F0FDF4')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F0FDF4')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(dt)
    elements.append(Spacer(1, 0.5*cm))

    # Items Table
    elements.append(Paragraph("<b>Items Ordered</b>", styles['Heading3']))
    items_data = [['Item Name', 'Category', 'Price (₹)', 'Quantity', 'Subtotal (₹)']]
    for item in order.items.all():
        items_data.append([
            item.food_item.name,
            item.food_item.get_category_display(),
            f"{item.unit_price:.2f}",
            str(item.quantity),
            f"{item.subtotal:.2f}"
        ])
    items_data.append(['Total', '', '', '', f"{order.total_amount:.2f}"])
    
    it = Table(items_data, colWidths=[6.5*cm, 3.5*cm, 2.5*cm, 2*cm, 2.5*cm])
    it.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#10B981')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F0FDF4')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(it)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0')))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(
        "<font size=8 color='#64748B'>Thank you for ordering at Campus Food Court! Collect your order at the food court counter.</font>",
        ParagraphStyle('footer', alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Food_Order_{order.pk}.pdf"'
    return response


@admin_required
def food_orders_export_pdf(request):
    orders = FoodOrder.objects.select_related('student').prefetch_related('items__food_item').order_by('-ordered_at')
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

    elements.append(Paragraph("<font size=18><b>Campus Food Court — Admin Report</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=10 color='#64748B'>Summary of all food orders placed</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#10B981')))
    elements.append(Spacer(1, 0.4*cm))

    table_data = [['Order #', 'Student', 'Roll No', 'Total Amount', 'Payment', 'Order Status', 'Date']]
    total_rev = Decimal('0')
    for ord in orders:
        table_data.append([
            f"#{ord.pk}",
            ord.student.full_name,
            ord.student.roll_number,
            f"₹{ord.total_amount:.2f}",
            ord.get_payment_status_display(),
            ord.get_order_status_display(),
            ord.ordered_at.strftime('%d %b %Y %H:%M')
        ])
        if ord.payment_status == 'paid':
            total_rev += ord.total_amount
            
    table_data.append(['Total Collected', '', '', f"₹{total_rev:.2f}", '', '', ''])

    t = Table(table_data, colWidths=[1.5*cm, 4*cm, 2.5*cm, 2.5*cm, 2.2*cm, 2.3*cm, 3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#10B981')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F0FDF4')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Food_Orders_Report.pdf"'
    return response


@login_required
def laundry_order_receipt_pdf(request, pk):
    from .models import LaundryOrder
    order = get_object_or_404(LaundryOrder, pk=pk)
    if not _verify_student_or_admin(request, order.student):
        raise PermissionDenied
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

    elements.append(Paragraph("<font size=20><b>EduAdmin Campus Laundry Service</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=11 color='#3B82F6'>Laundry Payment Receipt / Invoice</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3B82F6')))
    elements.append(Spacer(1, 0.4*cm))

    details = [
        ['Order Number', order.order_number or f'#{order.pk}', 'Date', order.ordered_at.strftime('%d %b %Y %H:%M')],
        ['Student Name', order.student.full_name, 'Roll Number', order.student.roll_number],
        ['Payment Status', order.get_payment_status_display(), 'Order Status', order.get_status_display()],
        ['Transaction ID', order.transaction_id or '—', 'UPI ID', order.upi_id or '—'],
        ['Pickup Date', order.pickup_date.strftime('%d %b %Y') if order.pickup_date else '—', 'Room Number', order.room_number or '—'],
    ]
    dt = Table(details, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#EFF6FF')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(dt)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("<b>Laundry Items Details</b>", styles['Heading3']))
    items_data = [['Service / Item Type', 'Category', 'Rate (₹)', 'Quantity', 'Subtotal (₹)']]
    for item in order.items.all():
        items_data.append([
            item.service.name,
            item.service.get_category_display(),
            f"{item.unit_price:.2f}",
            str(item.quantity),
            f"{item.subtotal:.2f}"
        ])
    items_data.append(['Total Amount', '', '', '', f"{order.total_amount:.2f}"])
    
    it = Table(items_data, colWidths=[6.5*cm, 3.5*cm, 2.5*cm, 2*cm, 2.5*cm])
    it.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EFF6FF')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(it)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0')))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(
        f"<font size=8 color='#64748B'>For status tracking or delivery coordination, contact Campus Laundry Services | Instructions: {order.special_instructions or 'None'}</font>",
        ParagraphStyle('footer', alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Laundry_Receipt_{order.order_number}.pdf"'
    return response


@admin_required
def laundry_orders_export_pdf(request):
    from .models import LaundryOrder
    orders = LaundryOrder.objects.select_related('student').prefetch_related('items__service').order_by('-ordered_at')
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

    elements.append(Paragraph("<font size=18><b>Campus Laundry Orders — Admin Report</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=10 color='#64748B'>Summary of all laundry orders</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6')))
    elements.append(Spacer(1, 0.4*cm))

    table_data = [['Order #', 'Student', 'Roll No', 'Total Amount', 'Payment', 'Order Status', 'Date']]
    total_rev = Decimal('0')
    for ord in orders:
        table_data.append([
            ord.order_number,
            ord.student.full_name,
            ord.student.roll_number,
            f"₹{ord.total_amount:.2f}",
            ord.get_payment_status_display(),
            ord.get_status_display(),
            ord.ordered_at.strftime('%d %b %Y')
        ])
        if ord.payment_status == 'paid':
            total_rev += ord.total_amount
            
    table_data.append(['Total Revenue', '', '', f"₹{total_rev:.2f}", '', '', ''])

    t = Table(table_data, colWidths=[2.2*cm, 4*cm, 2.5*cm, 2.3*cm, 2.2*cm, 2.3*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EFF6FF')),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Laundry_Orders_Report.pdf"'
    return response


@admin_required
def result_export_pdf(request):
    results = Result.objects.select_related('student', 'course').order_by('-created_at')
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

    elements.append(Paragraph("<font size=18><b>Student Academic Results Report</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=10 color='#64748B'>Comprehensive results registry</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4F46E5')))
    elements.append(Spacer(1, 0.4*cm))

    table_data = [['Student Name', 'Roll No', 'Course', 'Semester', 'Marks', 'Grade']]
    for res in results:
        table_data.append([
            res.student.full_name,
            res.student.roll_number,
            res.course.name,
            res.semester,
            f"{res.marks_obtained}/{res.total_marks}",
            res.grade or '—'
        ])

    t = Table(table_data, colWidths=[4.5*cm, 2.5*cm, 5*cm, 2.5*cm, 2*cm, 1.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Results_Report.pdf"'
    return response


@admin_required
def attendance_export_pdf(request):
    records = AttendanceRecord.objects.select_related('student').order_by('-date')
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

    elements.append(Paragraph("<font size=18><b>Student Attendance Summary Report</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=10 color='#64748B'>Full attendance record log</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=6)))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#EA580C')))
    elements.append(Spacer(1, 0.4*cm))

    table_data = [['Student Name', 'Roll No', 'Date', 'Status', 'Remarks']]
    for rec in records:
        table_data.append([
            rec.student.full_name,
            rec.student.roll_number,
            rec.date.strftime('%d %b %Y'),
            rec.status.title(),
            rec.remarks or '—'
        ])

    t = Table(table_data, colWidths=[5*cm, 3*cm, 3*cm, 2.5*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EA580C')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Attendance_Report.pdf"'
    return response


@admin_required
def send_fee_reminder(request, pk):
    fee = get_object_or_404(FeeRecord, pk=pk)
    due = fee.total_due()
    if due <= 0:
        messages.warning(request, "Fee is already fully paid. No reminder sent.")
        return redirect('fee_list')
        
    user = User.objects.filter(email=fee.student.email).first()
    if user:
        Notification.objects.create(
            user=user,
            notif_type='fee_due',
            title='Outstanding Fee Reminder',
            message=f'Dear Student, this is a reminder that you have a pending fee of ₹{due:.2f} due by {fee.due_date or "—"}. Please pay as soon as possible.',
            link='/payments/',
            priority='high'
        )
        messages.success(request, f"Fee reminder sent successfully to student: {fee.student.full_name}.")
    else:
        messages.error(request, f"No user account linked to email {fee.student.email}. Could not send reminder.")
        
    return redirect('fee_list')


@admin_required
def send_assignment_reminder(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    students = Student.objects.filter(status='active')
    if assignment.course:
        students = students.filter(course=assignment.course)
    elif assignment.course and assignment.course.department:
        students = students.filter(department=assignment.course.department)
        
    student_emails = students.values_list('email', flat=True)
    users = User.objects.filter(email__in=student_emails)
    
    if users.exists():
        Notification.broadcast(
            users=users,
            message=f"Reminder: Assignment '{assignment.title}' is due on {assignment.due_date or '—'}. Please submit it on time.",
            notif_type='assignment',
            title='Assignment Deadline Reminder',
            link='/assignments/',
            priority='high'
        )
        messages.success(request, f"Assignment reminder broadcasted to {users.count()} students.")
    else:
        messages.warning(request, "No registered student users found for this assignment.")
        
    return redirect('assignment_list')


@login_required
def student_id_card_pdf(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not _verify_student_or_admin(request, student):
        raise PermissionDenied

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Title / Top
    elements.append(Paragraph("<font size=16 color='#2563EB'><b>EduAdmin University</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=2)))
    elements.append(Paragraph("<b>STUDENT IDENTIFICATION CARD</b>", ParagraphStyle('card_title', alignment=TA_CENTER, fontSize=10, textColor=colors.HexColor('#64748B'), spaceAfter=15)))

    card_photo = None
    if student.photo:
        try:
            card_photo = Image(student.photo.path, width=3*cm, height=3.5*cm)
        except Exception:
            card_photo = Paragraph("<font color='#64748B'>[Photo]</font>", styles['Normal'])
    else:
        card_photo = Paragraph("<font color='#64748B'>[No Photo]</font>", styles['Normal'])

    student_details = [
        [Paragraph(f"<b>Name:</b> {student.full_name}", styles['Normal'])],
        [Paragraph(f"<b>ID:</b> {student.student_id}", styles['Normal'])],
        [Paragraph(f"<b>Roll No:</b> {student.roll_number}", styles['Normal'])],
        [Paragraph(f"<b>Dept:</b> {student.department.name if student.department else '—'}", styles['Normal'])],
        [Paragraph(f"<b>Course:</b> {student.course.name if student.course else '—'}", styles['Normal'])],
        [Paragraph(f"<b>DOB:</b> {student.date_of_birth.strftime('%d %b %Y') if student.date_of_birth else '—'}", styles['Normal'])],
    ]
    details_table = Table(student_details, colWidths=[8*cm])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))

    card_data = [
        [card_photo, details_table]
    ]
    card_table = Table(card_data, colWidths=[3.5*cm, 8.5*cm])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#2563EB')),
        ('PADDING', (0,0), (-1,-1), 15),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0, colors.white),
    ]))
    
    outer_table = Table([[card_table]], colWidths=[12.5*cm])
    outer_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(outer_table)
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph("<font size=8 color='#94A3B8'>Valid only when accompanied by official fee payment slip. Return if found to: Registrar, EduAdmin Campus.</font>", ParagraphStyle('f', alignment=TA_CENTER)))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ID_Card_{student.roll_number}.pdf"'
    return response


@login_required
def student_marksheet_pdf(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not _verify_student_or_admin(request, student):
        raise PermissionDenied

    results = student.results.select_related('course').order_by('semester', 'course__name')
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

    # Header
    elements.append(Paragraph("<font size=22><b>EduAdmin University</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<b>OFFICIAL GRADE SHEET / TRANSCRIPT</b>", ParagraphStyle('sub', alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#4F46E5'), spaceAfter=8)))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4F46E5')))
    elements.append(Spacer(1, 0.4*cm))

    # Student details
    info_data = [
        ['Student Name', student.full_name, 'Roll Number', student.roll_number],
        ['Student ID', student.student_id, 'Department', student.department.name if student.department else '—'],
        ['Course/Program', student.course.name if student.course else '—', 'Current CGPA', f"{student.cgpa:.2f}"],
    ]
    it = Table(info_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    it.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(it)
    elements.append(Spacer(1, 0.5*cm))

    # Results Table
    elements.append(Paragraph("<b>Academic Results</b>", styles['Heading3']))
    res_data = [['Course Code', 'Course Name', 'Semester', 'Marks Obtained', 'Total Marks', 'Grade']]
    for r in results:
        res_data.append([
            r.course.code,
            r.course.name,
            r.semester,
            f"{r.marks_obtained:.1f}",
            f"{r.total_marks:.1f}",
            r.grade
        ])
        
    rt = Table(res_data, colWidths=[2.5*cm, 6.5*cm, 2.5*cm, 2.5*cm, 2*cm, 1*cm])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('ALIGN', (3,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(rt)
    elements.append(Spacer(1, 0.5*cm))

    # Summary box
    summary_data = [
        ['Overall Performance Status', 'PASS' if student.cgpa >= 2.0 else 'FAIL', 'CGPA', f"{student.cgpa:.2f}"]
    ]
    st = Table(summary_data, colWidths=[6*cm, 3*cm, 3*cm, 5*cm])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0FDF4') if student.cgpa >= 2.0 else colors.HexColor('#FEF2F2')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1,0), (1,0), colors.HexColor('#16A34A') if student.cgpa >= 2.0 else colors.HexColor('#DC2626')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BBF7D0') if student.cgpa >= 2.0 else colors.HexColor('#FECACA')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 1*cm))

    # Signatures
    sig_data = [
        ['Prepared By', 'Checked By', 'Controller of Examinations']
    ]
    sigt = Table(sig_data, colWidths=[5.6*cm, 5.6*cm, 5.8*cm])
    sigt.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 40),
    ]))
    elements.append(sigt)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Marksheet_{student.roll_number}.pdf"'
    return response


@login_required
def student_bonafide_pdf(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not _verify_student_or_admin(request, student):
        raise PermissionDenied

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2.5*cm, leftMargin=2.5*cm, topMargin=2.5*cm, bottomMargin=2.5*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Letterhead / Title
    elements.append(Paragraph("<font size=24><b>EduAdmin University</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<font size=10 color='#64748B'>Accredited Grade A+ University | info@eduadmin.edu</font>", ParagraphStyle('sub', alignment=TA_CENTER, spaceAfter=12)))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1E3A8A')))
    elements.append(Spacer(1, 0.8*cm))

    # Date
    today = date.today().strftime('%d %B %Y')
    elements.append(Paragraph(f"<b>Date:</b> {today}", ParagraphStyle('d', alignment=TA_RIGHT, spaceAfter=20)))

    # Title of Certificate
    elements.append(Paragraph("<font size=16><b>BONAFIDE CERTIFICATE</b></font>", ParagraphStyle('cert', alignment=TA_CENTER, spaceAfter=25)))

    # Certificate body
    gender_pronoun = "He" if student.gender == 'male' else "She"
    pos_pronoun = "his" if student.gender == 'male' else "her"
    
    body_text = (
        f"This is to certify that <b>{student.full_name}</b>, Roll Number <b>{student.roll_number}</b>, "
        f"is a bonafide student of this institution. {gender_pronoun} is currently studying in the "
        f"department of <b>{student.department.name if student.department else '—'}</b>, pursuing "
        f"the course <b>{student.course.name if student.course else '—'}</b> for the academic year "
        f"<b>{student.year_of_admission}-{str(student.year_of_admission+1)[2:]}</b>."
    )
    elements.append(Paragraph(body_text, ParagraphStyle('body', alignment=TA_JUSTIFY, fontSize=12, leading=18, spaceAfter=20)))
    
    body_text_2 = (
        f"To the best of our knowledge, {pos_pronoun} character and conduct have been exemplary "
        f"during {pos_pronoun} tenure at this institution. This certificate is being issued at the request of "
        f"the student for official or academic verification purposes."
    )
    elements.append(Paragraph(body_text_2, ParagraphStyle('body2', alignment=TA_JUSTIFY, fontSize=12, leading=18, spaceAfter=40)))

    elements.append(Spacer(1, 1.5*cm))

    # Signature
    sig_data = [
        ['', 'Registrar / Dean of Students']
    ]
    sigt = Table(sig_data, colWidths=[10*cm, 6*cm])
    sigt.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (1,0), (1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (1,0), (1,0), 10),
        ('TOPPADDING', (1,0), (1,0), 30),
    ]))
    elements.append(sigt)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Bonafide_Certificate_{student.roll_number}.pdf"'
    return response


@login_required
def exam_hall_ticket_pdf(request, pk):
    app = get_object_or_404(ExamApplication, pk=pk, status='approved')
    if not _verify_student_or_admin(request, app.student):
        raise PermissionDenied

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

    # Header
    elements.append(Paragraph("<font size=20><b>EduAdmin University</b></font>", ParagraphStyle('h', alignment=TA_CENTER, spaceAfter=4)))
    elements.append(Paragraph("<b>EXAMINATION ADMIT CARD / HALL TICKET</b>", ParagraphStyle('sub', alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#DC2626'), spaceAfter=8)))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#DC2626')))
    elements.append(Spacer(1, 0.4*cm))

    # Student and Exam details
    details_data = [
        ['Student Name', app.student.full_name, 'Roll Number', app.student.roll_number],
        ['Hall Ticket No', app.hall_ticket_no or '—', 'Exam Title', app.exam.title],
        ['Course Code', app.exam.course.code if app.exam.course else '—', 'Department', app.student.department.name if app.student.department else '—'],
        ['Exam Date', app.exam.exam_date.strftime('%d %b %Y'), 'Timings', f"{app.exam.start_time.strftime('%I:%M %p')} - {app.exam.end_time.strftime('%I:%M %p')}"],
        ['Exam Venue', app.exam.venue or 'Main Hall', 'Duration', f"{app.exam.duration_mins} Minutes"],
    ]
    dt = Table(details_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#FEF2F2')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#FEF2F2')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(dt)
    elements.append(Spacer(1, 0.6*cm))

    # Instructions
    elements.append(Paragraph("<b>Candidate Instructions:</b>", styles['Heading4']))
    instructions = (
        "1. Candidates must produce this Admit Card to enter the examination hall.<br/>"
        "2. Please report to the examination hall at least 15 minutes before the start time.<br/>"
        "3. Mobile phones, programmable calculators, or any electronic gadgets are strictly prohibited.<br/>"
        "4. Any candidate violating exam regulations will be disqualified immediately."
    )
    elements.append(Paragraph(instructions, ParagraphStyle('ins', fontSize=9, leading=14, textColor=colors.HexColor('#475569'), spaceAfter=20)))

    elements.append(Spacer(1, 1.5*cm))

    # Signatures
    sig_data = [
        ['Candidate Signature', 'Controller of Examinations']
    ]
    sigt = Table(sig_data, colWidths=[8.5*cm, 8.5*cm])
    sigt.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 35),
    ]))
    elements.append(sigt)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Hall_Ticket_{app.hall_ticket_no}.pdf"'
    return response


@login_required
def search_everywhere(request):
    query = request.GET.get('q', '').strip()
    results = {
        'query': query,
        'students': [],
        'courses': [],
        'notices': [],
        'routes': [],
        'books': [],
        'teachers': [],
        'total_count': 0
    }
    
    if query:
        results['students'] = Student.objects.filter(
            Q(full_name__icontains=query) | Q(roll_number__icontains=query) | Q(student_id__icontains=query)
        ).select_related('department')[:10]
        
        results['courses'] = Course.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        ).select_related('department')[:10]
        
        results['notices'] = Notice.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )[:10]
        
        from transport.models import BusRoute
        results['routes'] = BusRoute.objects.filter(
            Q(route_number__icontains=query) | Q(route_name__icontains=query) | Q(start_point__icontains=query) | Q(end_point__icontains=query)
        )[:10]
        
        results['books'] = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query)
        )[:10]
        
        results['teachers'] = Teacher.objects.filter(
            Q(name__icontains=query) | Q(subjects_handling__icontains=query)
        )[:10]
        
        results['total_count'] = (
            len(results['students']) + len(results['courses']) + len(results['notices']) +
            len(results['routes']) + len(results['books']) + len(results['teachers'])
        )
        
    return render(request, 'dashboard/search_results.html', results)

