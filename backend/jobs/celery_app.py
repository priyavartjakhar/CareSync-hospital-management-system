from celery import Celery
from celery.schedules import crontab
import os

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

celery_app = Celery('hms_jobs', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery_app.conf.timezone = os.environ.get('APP_TIMEZONE', 'Asia/Kolkata')
celery_app.conf.beat_schedule = {
    'daily-reminders-8am': {
        'task': 'backend.jobs.tasks.daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-doctor-report-midnight': {
        'task': 'backend.jobs.tasks.monthly_report',
        'schedule': crontab(day_of_month=30, hour=0, minute=0),
    },
}
