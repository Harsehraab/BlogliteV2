from celery_conf import cly
from celery.schedules import crontab
from appnew import User, Post, LastLogin
import appnew

cly.conf.beat_schedule = {
    'send_emails_every_30_secs': {
        'task': 'appnew.send_emails_every_30_secs',
        'schedule': crontab('*/1','*','*','*','*')
    },
    'scheduled_task': {
        'task': 'appnew.schduled_task',
        'schedule': crontab(hour=17, minute=0, day_of_week='*')
    }
}