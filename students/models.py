from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    head = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def student_count(self):
        return self.student_set.count()


class Course(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
    ]

    # Auto-generated student ID
    student_id = models.CharField(max_length=20, unique=True, blank=True)

    # Personal Info
    full_name = models.CharField(max_length=150)
    roll_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='students/photos/', null=True, blank=True)

    # Academic Info
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    year_of_admission = models.IntegerField(default=timezone.now().year)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Performance
    semester_gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    class_rank = models.PositiveIntegerField(null=True, blank=True)
    pass_fail_status = models.CharField(
        max_length=10,
        choices=[('pass', 'Pass'), ('fail', 'Fail')],
        default='pass'
    )
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    performance_prediction = models.CharField(max_length=120, blank=True)
    attendance_prediction = models.CharField(max_length=120, blank=True)
    risk_level = models.CharField(
        max_length=12,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='low'
    )

    # Parent Details
    parent_name = models.CharField(max_length=150, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.roll_number})"

    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate unique student ID: STU-YYYY-XXXX
            year = timezone.now().year
            uid = str(uuid.uuid4()).upper()[:4]
            self.student_id = f"STU-{year}-{uid}"
        super().save(*args, **kwargs)

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/img/default-student.png'

    def get_gpa_badge(self):
        gpa = float(self.gpa)
        if gpa >= 3.5:
            return 'success'
        elif gpa >= 2.5:
            return 'warning'
        else:
            return 'danger'

    def get_attendance_badge(self):
        att = float(self.attendance_percentage)
        if att >= 75:
            return 'success'
        elif att >= 60:
            return 'warning'
        else:
            return 'danger'


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"


class Result(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D', 'D'), ('F', 'F'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.course.name} - {self.grade}"

    def percentage(self):
        if self.total_marks > 0:
            return round((self.marks_obtained / self.total_marks) * 100, 2)
        return 0


class Teacher(models.Model):
    name = models.CharField(max_length=150)
    qualification = models.CharField(max_length=150, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    subjects_handling = models.TextField(blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TimetableEntry(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
    ]
    day = models.CharField(max_length=10, choices=DAY_CHOICES, default='Monday')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')} - {self.course or 'TBA'}"


class Assignment(models.Model):
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    assignment_file = models.FileField(upload_to='assignments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('pending', 'Pending'),
        ('late', 'Late'),
    ]
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_file = models.FileField(upload_to='assignment_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')

    def __str__(self):
        return f"{self.assignment.title} — {self.student.full_name}"


class Notice(models.Model):
    NOTICE_CHOICES = [
        ('exam', 'Exam Notification'),
        ('holiday', 'Holiday Notice'),
        ('placement', 'Placement Update'),
        ('general', 'General'),
    ]
    title = models.CharField(max_length=180)
    notice_type = models.CharField(max_length=20, choices=NOTICE_CHOICES, default='general')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FeeRecord(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hostel_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_due(self):
        amount = self.tuition_fee + self.exam_fee + self.hostel_fee
        return amount - self.paid_amount

    def __str__(self):
        return f"{self.student.full_name} — {self.get_status_display()}"


class PaymentTransaction(models.Model):
    METHOD_CHOICES = [
        ('upi',          'UPI'),
        ('razorpay',     'Razorpay'),
        ('qr_code',      'QR Code'),
        ('cash',         'Cash'),
        ('bank_transfer','Bank Transfer'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    ]
    fee_record      = models.ForeignKey(FeeRecord, on_delete=models.CASCADE, related_name='payments')
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    method          = models.CharField(max_length=20, choices=METHOD_CHOICES, default='upi')
    upi_id          = models.CharField(max_length=120, blank=True)
    transaction_ref = models.CharField(max_length=120, blank=True)  # UPI / bank ref
    razorpay_order_id    = models.CharField(max_length=120, blank=True)
    razorpay_payment_id  = models.CharField(max_length=120, blank=True)
    razorpay_signature   = models.CharField(max_length=255, blank=True)
    status          = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    paid_at         = models.DateTimeField(null=True, blank=True)
    paid_by         = models.CharField(max_length=150, blank=True)
    receipt_number  = models.CharField(max_length=40, blank=True, unique=True, null=True)
    notes           = models.TextField(blank=True)
    approved_by     = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payments'
    )
    approved_at     = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.fee_record.student.full_name} — ₹{self.amount} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.receipt_number and self.status == 'completed':
            import uuid as _uuid
            self.receipt_number = f"RCPT-{str(_uuid.uuid4()).upper()[:10]}"
        super().save(*args, **kwargs)


class Notification(models.Model):
    TYPE_CHOICES = [
        ('fee_due',        'Fee Due Alert'),
        ('fee_paid',       'Fee Payment Confirmed'),
        ('assignment',     'Assignment Deadline'),
        ('attendance',     'Attendance Warning'),
        ('result',         'Result Published'),
        ('exam',           'Exam Notification'),
        ('transport',      'Transport Alert'),
        ('announcement',   'General Announcement'),
        ('system',         'System'),
    ]
    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type   = models.CharField(max_length=20, choices=TYPE_CHOICES, default='announcement')
    title        = models.CharField(max_length=120, blank=True)
    message      = models.CharField(max_length=500)
    is_read      = models.BooleanField(default=False)
    priority     = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    link         = models.CharField(max_length=255, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] {self.user.username} — {self.message[:50]}"

    def icon(self):
        icons = {
            'fee_due':      '💳',
            'fee_paid':     '✅',
            'assignment':   '📝',
            'attendance':   '⚠️',
            'result':       '📊',
            'exam':         '📋',
            'transport':    '🚌',
            'announcement': '📢',
            'system':       '⚙️',
        }
        return icons.get(self.notif_type, '🔔')

    def color(self):
        colors = {
            'fee_due':      'warning',
            'fee_paid':     'success',
            'assignment':   'primary',
            'attendance':   'danger',
            'result':       'success',
            'exam':         'purple',
            'transport':    'cyan',
            'announcement': 'primary',
            'system':       'secondary',
        }
        return colors.get(self.notif_type, 'primary')

    @classmethod
    def send(cls, user, message, notif_type='announcement', title='', link='', priority='medium'):
        """Helper to create a notification."""
        return cls.objects.create(
            user=user, message=message, notif_type=notif_type,
            title=title, link=link, priority=priority
        )

    @classmethod
    def broadcast(cls, users, message, notif_type='announcement', title='', link='', priority='medium'):
        """Send notification to multiple users."""
        objs = [
            cls(user=u, message=message, notif_type=notif_type,
                title=title, link=link, priority=priority)
            for u in users
        ]
        return cls.objects.bulk_create(objs)


# ═══════════════════════════════════════════════════════════════
#  ONLINE EXAM MODULE
# ═══════════════════════════════════════════════════════════════

class Exam(models.Model):
    EXAM_TYPE_CHOICES = [
        ('midterm',  'Mid-Term Exam'),
        ('final',    'Final Exam'),
        ('internal', 'Internal Assessment'),
        ('practical','Practical Exam'),
        ('entrance', 'Entrance Exam'),
    ]
    STATUS_CHOICES = [
        ('upcoming',   'Upcoming'),
        ('open',       'Applications Open'),
        ('closed',     'Applications Closed'),
        ('ongoing',    'Ongoing'),
        ('completed',  'Completed'),
        ('cancelled',  'Cancelled'),
    ]

    title          = models.CharField(max_length=200)
    exam_type      = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='midterm')
    course         = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    department     = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    description    = models.TextField(blank=True)

    # Schedule
    exam_date      = models.DateField()
    start_time     = models.TimeField()
    end_time       = models.TimeField()
    venue          = models.CharField(max_length=150, blank=True)
    duration_mins  = models.PositiveIntegerField(default=180, help_text='Duration in minutes')

    # Application window
    apply_start    = models.DateField()
    apply_end      = models.DateField()

    # Fee
    exam_fee       = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    fee_required   = models.BooleanField(default=True)

    # Seats
    total_seats    = models.PositiveIntegerField(default=100)

    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-exam_date']

    def __str__(self):
        return f"{self.title} — {self.exam_date}"

    def seats_available(self):
        filled = self.applications.filter(
            status__in=['approved', 'pending']
        ).count()
        return max(self.total_seats - filled, 0)

    def total_applicants(self):
        return self.applications.count()

    def is_application_open(self):
        from datetime import date
        today = date.today()
        return self.apply_start <= today <= self.apply_end and self.status == 'open'

    def fee_collected(self):
        from django.db.models import Sum
        total = self.applications.filter(
            payment_status='paid'
        ).aggregate(s=Sum('fee_paid'))['s'] or 0
        return total


class ExamApplication(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending Review'),
        ('approved',  'Approved'),
        ('rejected',  'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('unpaid',    'Unpaid'),
        ('paid',      'Paid'),
        ('waived',    'Waived'),
        ('refunded',  'Refunded'),
    ]

    exam            = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='applications')
    student         = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_applications')

    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status  = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='unpaid')
    fee_paid        = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Payment details
    transaction_id  = models.CharField(max_length=100, blank=True)
    upi_id          = models.CharField(max_length=100, blank=True)
    paid_at         = models.DateTimeField(null=True, blank=True)

    # Hall ticket
    hall_ticket_no  = models.CharField(max_length=30, blank=True, unique=True, null=True)

    # Remarks
    remarks         = models.TextField(blank=True)
    applied_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['exam', 'student']
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.full_name} → {self.exam.title}"

    def save(self, *args, **kwargs):
        # Auto-generate hall ticket number on approval
        if self.status == 'approved' and not self.hall_ticket_no:
            uid = str(uuid.uuid4()).upper()[:6]
            self.hall_ticket_no = f"HT-{self.exam.pk:03d}-{uid}"
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════
#  CAMPUS FOOD COURT
# ═══════════════════════════════════════════════════════════════

class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ('meal', 'Meals'),
        ('snack', 'Snacks'),
        ('beverage', 'Beverages'),
        ('dessert', 'Desserts'),
    ]
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='meal')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    emoji = models.CharField(max_length=8, default='🍽️')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} — ₹{self.price}"


class FoodOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Order Received'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='food_orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='unpaid')
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    upi_id = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    pickup_note = models.CharField(max_length=200, blank=True, default='Collect at Campus Food Court counter')
    ordered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ordered_at']

    def __str__(self):
        return f"Order #{self.pk} — {self.student.full_name} (₹{self.total_amount})"


class FoodOrderItem(models.Model):
    order = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"


# ═══════════════════════════════════════════════════════════════
#  LIBRARY MANAGEMENT MODULE
# ═══════════════════════════════════════════════════════════════

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"


class BookIssue(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_issues')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='issued')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']
        # Allow same student to borrow same book multiple times but not on same day
        unique_together = ['book', 'student', 'issue_date']

    def __str__(self):
        return f"{self.book.title} → {self.student.full_name}"

    def is_overdue(self):
        if self.status == 'returned' or self.return_date:
            return False
        from datetime import date
        return date.today() > self.due_date

    def current_fine(self):
        if self.return_date or self.status == 'returned':
            return self.fine_amount
        from datetime import date
        from decimal import Decimal
        today = date.today()
        if today > self.due_date:
            days = (today - self.due_date).days
            return Decimal(days * 5)  # ₹5 per day
        return Decimal(0)


# ═══════════════════════════════════════════════════════════════
#  HOSTEL MANAGEMENT MODULE
# ═══════════════════════════════════════════════════════════════

class HostelRoom(models.Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single Room'),
        ('double', 'Double Sharing'),
        ('triple', 'Triple Sharing'),
        ('quad',   'Four Bed Sharing'),
    ]

    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='double')
    capacity = models.PositiveIntegerField(default=2)
    current_occupancy = models.PositiveIntegerField(default=0)
    fee_per_semester = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['room_number']

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()})"

    def available_beds(self):
        return max(self.capacity - self.current_occupancy, 0)

    def is_available(self):
        return self.current_occupancy < self.capacity


class RoomAllocation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('checked_out', 'Checked Out'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='room_allocations')
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name='allocations')
    allocated_date = models.DateField(default=timezone.now)
    checkout_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-allocated_date']

    def __str__(self):
        return f"{self.student.full_name} in Room {self.room.room_number}"



# ═══════════════════════════════════════════════════════════════
#  LAUNDRY MANAGEMENT MODULE
# ═══════════════════════════════════════════════════════════════

class LaundryService(models.Model):
    """Individual laundry services with per-item pricing."""
    CATEGORY_CHOICES = [
        ('washing',   'Washing'),
        ('drying',    'Drying'),
        ('ironing',   'Ironing'),
        ('folding',   'Folding'),
        ('bedding',   'Bed & Pillow'),
        ('towels',    'Towels & Cleaning'),
        ('special',   'Special Care'),
    ]

    name          = models.CharField(max_length=120)
    category      = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description   = models.CharField(max_length=255, blank=True)
    price_per_item= models.DecimalField(max_digits=8, decimal_places=2)
    unit          = models.CharField(max_length=30, default='per piece',
                                     help_text='e.g. per piece, per kg, per pair')
    turnaround_hrs= models.PositiveIntegerField(default=24,
                                     help_text='Estimated delivery in hours')
    is_available  = models.BooleanField(default=True)
    emoji         = models.CharField(max_length=8, default='👕')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.emoji} {self.name} — ₹{self.price_per_item}/{self.unit}"


class LaundryOrder(models.Model):
    STATUS_CHOICES = [
        ('placed',      'Order Placed'),
        ('collected',   'Collected from Room'),
        ('processing',  'In Process'),
        ('ready',       'Ready for Pickup'),
        ('delivered',   'Delivered'),
        ('cancelled',   'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid',   'Paid'),
    ]

    student        = models.ForeignKey(Student, on_delete=models.CASCADE,
                                       related_name='laundry_orders')
    order_number   = models.CharField(max_length=20, unique=True, blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='unpaid')
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount    = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # UPI payment
    upi_id         = models.CharField(max_length=100, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at        = models.DateTimeField(null=True, blank=True)

    # Scheduling
    pickup_date    = models.DateField(null=True, blank=True)
    delivery_date  = models.DateField(null=True, blank=True)
    room_number    = models.CharField(max_length=30, blank=True)
    special_instructions = models.TextField(blank=True)

    ordered_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-ordered_at']

    def __str__(self):
        return f"Order #{self.order_number} — {self.student.full_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid as _uuid
            self.order_number = f"LDY-{str(_uuid.uuid4()).upper()[:8]}"
        super().save(*args, **kwargs)

    def balance_due(self):
        return self.total_amount - self.paid_amount


class LaundryOrderItem(models.Model):
    order      = models.ForeignKey(LaundryOrder, on_delete=models.CASCADE,
                                   related_name='items')
    service    = models.ForeignKey(LaundryService, on_delete=models.PROTECT)
    quantity   = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal   = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.service.name}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
