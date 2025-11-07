"""
Celery configuration for pdf_image_analyzer_backend project.
"""
import os
from kombu import Queue
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('pdf_image_analyzer_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Define task routes for each app - routes tasks to specific queues
app.conf.task_routes = {
    'apps.file_upload.tasks.*': {'queue': 'file_upload'},
    'apps.jobs.tasks.*': {'queue': 'jobs'},
    'apps.analytics.tasks.*': {'queue': 'analytics'},
}

# Define default queue
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'tasks'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'

# Explicitly define queues
app.conf.task_queues = (
    Queue('default', routing_key='default'),
    Queue('file_upload', routing_key='file_upload'),
    Queue('jobs', routing_key='jobs'),
    Queue('analytics', routing_key='analytics'),
)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

