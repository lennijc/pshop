import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'partyShop.settings')

app = Celery('partyShop')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'delete-expired-reservations-every-minute': {
        'task': 'base.tasks.delete_expired_reservations',
        'schedule': crontab(minute='*'),  # Run every minute
    },
}