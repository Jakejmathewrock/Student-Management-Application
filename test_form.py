import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    from accounts.forms import RegisterForm
    form = RegisterForm()
    print("RegisterForm initialized successfully!")
except Exception as e:
    print(f"Error: {e}")
