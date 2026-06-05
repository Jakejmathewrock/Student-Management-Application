import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()
try:
    response = client.get('/accounts/register/')
    print(f"Register status: {response.status_code}")
except Exception as e:
    print(f"Register Error: {e}")

try:
    response = client.get('/accounts/login/')
    print(f"Login status: {response.status_code}")
except Exception as e:
    print(f"Login Error: {e}")

try:
    response = client.get('/')
    print(f"Home status: {response.status_code}")
except Exception as e:
    print(f"Home Error: {e}")
