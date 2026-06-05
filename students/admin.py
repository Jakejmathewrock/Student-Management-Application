from django.contrib import admin
from .models import Student, Department, Course, AttendanceRecord, Result, Book, BookIssue, HostelRoom, RoomAllocation, Notification


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'credits']
    list_filter = ['department']
    search_fields = ['name', 'code']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'roll_number', 'department', 'course', 'gpa', 'status']
    list_filter = ['department', 'status', 'gender', 'year_of_admission']
    search_fields = ['full_name', 'roll_number', 'email', 'student_id']
    readonly_fields = ['student_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Personal Info', {
            'fields': ('student_id', 'full_name', 'roll_number', 'email', 'phone',
                       'date_of_birth', 'gender', 'address', 'photo')
        }),
        ('Academic Info', {
            'fields': ('department', 'course', 'year_of_admission', 'status')
        }),
        ('Performance', {
            'fields': ('gpa', 'attendance_percentage')
        }),
        ('Parent Details', {
            'fields': ('parent_name', 'parent_phone', 'parent_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'remarks']
    list_filter = ['status', 'date']
    search_fields = ['student__full_name']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'semester', 'marks_obtained', 'total_marks', 'grade']
    list_filter = ['semester', 'grade']
    search_fields = ['student__full_name', 'course__name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies', 'price']
    search_fields = ['title', 'author', 'isbn', 'category']
    list_filter = ['category']


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ['book', 'student', 'issue_date', 'due_date', 'return_date', 'status', 'fine_amount', 'fine_paid']
    list_filter = ['status', 'fine_paid', 'issue_date', 'due_date']
    search_fields = ['book__title', 'student__full_name', 'student__roll_number']


@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'capacity', 'current_occupancy', 'fee_per_semester']
    search_fields = ['room_number']
    list_filter = ['room_type']


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'allocated_date', 'checkout_date', 'status']
    list_filter = ['status', 'allocated_date']
    search_fields = ['student__full_name', 'room__room_number']




@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'notif_type', 'title', 'message_short', 'priority', 'is_read', 'created_at']
    list_filter   = ['notif_type', 'priority', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_editable = ['is_read']
    ordering      = ['-created_at']
    readonly_fields = ['created_at']
    actions       = ['mark_read', 'mark_unread', 'delete_selected']

    def message_short(self, obj):
        return obj.message[:60] + '…' if len(obj.message) > 60 else obj.message
    message_short.short_description = 'Message'

    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} notifications marked as read.')
    mark_read.short_description = 'Mark selected as read'

    def mark_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} notifications marked as unread.')
    mark_unread.short_description = 'Mark selected as unread'
