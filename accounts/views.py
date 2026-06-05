from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm, ProfileUpdateForm
from .models import UserProfile
from .utils import redirect_url_for_user


def _handle_login(request, allowed_roles, redirect_name, portal_label):
    """Authenticate and enforce role for student/parent/admin logins."""
    if request.user.is_authenticated:
        return redirect(redirect_url_for_user(request.user))

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                profile, _ = UserProfile.objects.get_or_create(user=user)
                role = 'admin' if user.is_superuser else profile.role
                if role not in allowed_roles and not (
                    'admin' in allowed_roles and user.is_superuser
                ):
                    messages.error(
                        request,
                        f'This account cannot sign in on the {portal_label} page. '
                        f'Use the correct login portal.'
                    )
                    return render(request, f'accounts/login_{redirect_name}.html', {
                        'form': form,
                        'portal_label': portal_label,
                    })
                login(request, user)
                messages.success(
                    request,
                    f'Welcome back, {user.first_name or user.username}!'
                )
                return redirect(redirect_url_for_user(user))
            messages.error(request, 'Invalid username or password.')

    return render(request, f'accounts/login_{redirect_name}.html', {
        'form': form,
        'portal_label': portal_label,
    })


def login_portal(request):
    """Choose admin, student, or parent login."""
    if request.user.is_authenticated:
        return redirect(redirect_url_for_user(request.user))
    return render(request, 'accounts/login_portal.html')


def login_view(request):
    return login_portal(request)


def login_admin(request):
    return _handle_login(
        request,
        allowed_roles=('admin', 'teacher'),
        redirect_name='admin',
        portal_label='Admin',
    )


def login_student(request):
    return _handle_login(
        request,
        allowed_roles=('student',),
        redirect_name='student',
        portal_label='Student',
    )


def login_parent(request):
    return _handle_login(
        request,
        allowed_roles=('parent',),
        redirect_name='parent',
        portal_label='Parent',
    )


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def register_view(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role='admin')
            messages.success(request, 'Account created! Please log in.')
            return redirect('login_admin')

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(
            instance=profile,
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        )

    template = 'accounts/profile.html'
    if profile.role in ('student', 'parent'):
        template = 'accounts/profile_portal.html'

    return render(request, template, {'form': form, 'profile': profile})
