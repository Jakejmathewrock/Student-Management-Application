import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()
try:
    response = client.post('/accounts/register/', {
        'username': 'testuser123',
        'email': 'test@example.com',
        'password': 'testpassword123',
        'password_confirm': 'testpassword123'
    })
    print(f"Register POST status: {response.status_code}")
except Exception as e:
    import traceback
    print(f"Register POST Error: {e}")
    traceback.print_exc()
