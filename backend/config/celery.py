"""
Celery configuration for MLBattle project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('mlbattle')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'fetch-kaggle-leaderboards': {
        'task': 'apps.submissions.tasks.fetch_all_active_competitions',
        'schedule': 300.0,  # Every 5 minutes
    },
    'update-competition-status': {
        'task': 'apps.competitions.tasks.update_competition_statuses',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
