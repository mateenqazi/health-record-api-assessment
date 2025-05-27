import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_record_api.settings')

app = Celery('health_record_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
