import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
client = Client()
try:
    user = User.objects.get(username='admin')
    client.force_login(user)
    urls_to_test = [
        '/',
        '/students/',
        '/students/add/',
        '/departments/',
        '/departments/add/',
        '/courses/',
        '/courses/add/',
        '/attendance/',
        '/attendance/add/',
        '/results/',
        '/results/add/',
        '/accounts/profile/',
    ]
    for url in urls_to_test:
        response = client.get(url)
        print(f"{url} -> {response.status_code}")
except Exception as e:
    import traceback
    traceback.print_exc()
