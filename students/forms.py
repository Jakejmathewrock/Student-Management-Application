from django import forms
from django.db.models import F
from .models import (
    FoodItem,
    Student, Department, Course, AttendanceRecord, Result,
    Teacher, TimetableEntry, Assignment, AssignmentSubmission,
    Notice, FeeRecord, Exam, ExamApplication, Book, BookIssue,
    HostelRoom, RoomAllocation, LaundryService,
)


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'full_name', 'roll_number', 'email', 'phone',
            'date_of_birth', 'gender', 'address', 'photo',
            'department', 'course', 'year_of_admission', 'status',
            'gpa', 'attendance_percentage',
            'parent_name', 'parent_phone', 'parent_email',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'year_of_admission': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '4'}),
            'attendance_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Parent's Full Name"}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Parent's Phone"}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Parent's Email"}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'head']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dept Code (e.g. CS)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'head': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Head'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'department', 'credits', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Code'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'date', 'status', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks'}),
        }


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'course', 'semester', 'marks_obtained', 'total_marks', 'grade', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Fall 2024'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class StudentSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, roll number, email...',
            'id': 'searchInput'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='All Departments',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Student.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    gender = forms.ChoiceField(
        choices=[('', 'All Genders')] + Student.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'qualification', 'experience_years', 'department', 'subjects_handling', 'salary']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teacher Name'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Qualification'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'subjects_handling': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Subject names separated by commas'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class TimetableForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['day', 'course', 'teacher', 'start_time', 'end_time', 'venue']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Classroom / Lab'}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'course', 'assigned_date', 'due_date', 'assignment_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignment title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'assigned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assignment_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['assignment', 'student', 'submitted_file', 'status']
        widgets = {
            'assignment': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'submitted_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'notice_type', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notice title'}),
            'notice_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class FeeRecordForm(forms.ModelForm):
    class Meta:
        model = FeeRecord
        fields = ['student', 'tuition_fee', 'exam_fee', 'hostel_fee', 'paid_amount', 'status', 'due_date']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'tuition_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'exam_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hostel_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PaymentForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'})
    )
    upi_id = forms.CharField(
        max_length=120,
        initial='eduadmin@upi',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter UPI ID'})
    )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Payment amount must be positive.')
        return amount


# ── Exam Forms ────────────────────────────────────────────────

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            'title', 'exam_type', 'course', 'department',
            'description', 'exam_date', 'start_time', 'end_time',
            'duration_mins', 'venue', 'apply_start', 'apply_end',
            'exam_fee', 'fee_required', 'total_seats', 'status',
        ]
        widgets = {
            'title':        forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Mid-Term CS101 Exam'}),
            'exam_type':    forms.Select(attrs={'class':'form-select'}),
            'course':       forms.Select(attrs={'class':'form-select'}),
            'department':   forms.Select(attrs={'class':'form-select'}),
            'description':  forms.Textarea(attrs={'class':'form-control','rows':3}),
            'exam_date':    forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'start_time':   forms.TimeInput(attrs={'class':'form-control','type':'time'}),
            'end_time':     forms.TimeInput(attrs={'class':'form-control','type':'time'}),
            'duration_mins':forms.NumberInput(attrs={'class':'form-control','min':'30'}),
            'venue':        forms.TextInput(attrs={'class':'form-control','placeholder':'Hall A / Online'}),
            'apply_start':  forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'apply_end':    forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'exam_fee':     forms.NumberInput(attrs={'class':'form-control','step':'0.01','min':'0'}),
            'fee_required': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'total_seats':  forms.NumberInput(attrs={'class':'form-control','min':'1'}),
            'status':       forms.Select(attrs={'class':'form-select'}),
        }


class ExamApplicationForm(forms.ModelForm):
    class Meta:
        model = ExamApplication
        fields = ['upi_id']
        widgets = {
            'upi_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'yourname@upi or yourname@paytm',
            }),
        }


class ExamPaymentForm(forms.Form):
    upi_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your UPI ID (e.g. name@paytm)',
        })
    )
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I confirm the payment of the exam fee shown above.'
    )


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'description', 'category', 'price', 'emoji', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'emoji': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '4'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FoodCourtPaymentForm(forms.Form):
    upi_id = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your UPI ID (e.g. name@paytm)',
        })
    )
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I confirm that I have paid the order total via UPI.',
    )


# ── Library Forms ─────────────────────────────────────────────

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book Title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author Name'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN (optional)'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category (e.g. Fiction, Reference, Technology)'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
        }


class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ['book', 'student', 'issue_date', 'due_date', 'remarks']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Remarks (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter books so that only those with available copies are shown
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)


# ── Hostel Forms ──────────────────────────────────────────────

class HostelRoomForm(forms.ModelForm):
    class Meta:
        model = HostelRoom
        fields = ['room_number', 'room_type', 'capacity', 'fee_per_semester', 'description']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A-101'}),
            'room_type': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fee_per_semester': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Room details...'}),
        }


class RoomAllocationForm(forms.ModelForm):
    class Meta:
        model = RoomAllocation
        fields = ['room', 'student', 'allocated_date', 'remarks']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'allocated_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter rooms to only show available ones (occupancy < capacity)
        self.fields['room'].queryset = HostelRoom.objects.filter(current_occupancy__lt=F('capacity'))
        
        # Filter students to only show those who do NOT have an active allocation currently
        allocated_student_ids = RoomAllocation.objects.filter(status='active').values_list('student_id', flat=True)
        self.fields['student'].queryset = Student.objects.exclude(id__in=allocated_student_ids).filter(status='active')




# ── Laundry Service Form ──────────────────────────────────────

class LaundryServiceForm(forms.ModelForm):
    class Meta:
        model = LaundryService
        fields = ['name', 'category', 'description', 'price_per_item', 'unit', 'turnaround_hrs', 'is_available', 'emoji']
        widgets = {
            'name':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service name'}),
            'category':       forms.Select(attrs={'class': 'form-select'}),
            'description':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description'}),
            'price_per_item': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'unit':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. per piece, per kg'}),
            'turnaround_hrs': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'is_available':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'emoji':          forms.TextInput(attrs={'class': 'form-control', 'maxlength': '4', 'placeholder': '👕'}),
        }
