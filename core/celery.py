# myproject/celery.py
import os
from celery import Celery

# Set default settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

# Namespace 'CELERY' ensures all Celery settings use the 'CELERY_' prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks.py files inside all registered apps
app.autodiscover_tasks()
