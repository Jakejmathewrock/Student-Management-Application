import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

client = Client()
try:
    response = client.get('/students/')
    print(f"Students status: {response.status_code}")
except Exception as e:
    import traceback
    traceback.print_exc()
