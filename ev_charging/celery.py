import os
from celery import Celery
"""
# this will tell Django to use the settings from the ev_charging project
# when configuring Celery
"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ev_charging.settings')

app = Celery('ev_charging')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()