import os
filepath = r"c:\Users\HP\OneDrive\Desktop\my project\student_project\students\views.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all @login_required with @admin_required
content = content.replace("@login_required", "@admin_required")

# Fix the import statement
old_import = "from django.contrib.auth.decorators import login_required"
new_import = "from django.contrib.auth.decorators import login_required\nfrom accounts.decorators import admin_required, student_required"
content = content.replace(old_import, new_import)

# Append the student_dashboard view
student_view = """

# ─── Student Portal ───────────────────────────────────────────────────────────

@student_required
def student_dashboard(request):
    try:
        # Get the student record associated with the logged-in user
        student = Student.objects.get(email=request.user.email)
        attendance_records = student.attendance_records.order_by('-date')[:5]
        results = student.results.select_related('course').order_by('-created_at')
        
        context = {
            'student': student,
            'attendance_records': attendance_records,
            'results': results,
        }
    except Student.DoesNotExist:
        context = {
            'error': 'Your student profile has not been linked yet. Please contact the administration.'
        }
        
    return render(request, 'dashboard/student_dashboard.html', context)
"""

content += student_view

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated students/views.py successfully.")
