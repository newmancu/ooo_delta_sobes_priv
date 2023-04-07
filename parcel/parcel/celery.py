import os
from celery import Celery
# from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parcel.settings')

app = Celery('parcel')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# TODO: REMOVE default debug_task
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# app.conf.beat_schedule = {
#     'every': { 
#         'task': 'parcel_api.tasks.perodic_update',
#         'schedule': crontab(minute='*/1'),
#     },
# }