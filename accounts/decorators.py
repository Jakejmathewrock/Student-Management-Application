from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def _get_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return 'admin'
    if hasattr(user, 'profile'):
        return user.profile.role
    return None


def admin_required(view_func):
    """Require admin, teacher, or superuser."""
    def check_user(user):
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        role = _get_role(user)
        if role in ('admin', 'teacher'):
            return True
        raise PermissionDenied
    return user_passes_test(check_user, login_url='login_admin')(view_func)


def student_required(view_func):
    """Require student role."""
    def check_user(user):
        if not user.is_authenticated:
            return False
        if _get_role(user) == 'student':
            return True
        raise PermissionDenied
    return user_passes_test(check_user, login_url='login_student')(view_func)


def parent_required(view_func):
    """Require parent role."""
    def check_user(user):
        if not user.is_authenticated:
            return False
        if _get_role(user) == 'parent':
            return True
        raise PermissionDenied
    return user_passes_test(check_user, login_url='login_parent')(view_func)


def portal_user_required(view_func):
    """Student or parent only (for shared portal pages)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        role = _get_role(request.user)
        if role not in ('student', 'parent'):
            messages.error(request, 'This page is for students and parents only.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
