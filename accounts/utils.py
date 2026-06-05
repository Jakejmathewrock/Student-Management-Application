"""Auth helpers for role-based redirects."""

def redirect_url_for_user(user):
    if not user.is_authenticated:
        return 'login'
    if user.is_superuser:
        return 'dashboard'
    profile = getattr(user, 'profile', None)
    if profile is None:
        return 'dashboard'
    role = profile.role
    if role == 'student':
        return 'student_dashboard'
    if role == 'parent':
        return 'parent_dashboard'
    return 'dashboard'
