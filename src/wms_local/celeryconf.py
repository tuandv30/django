import os
from celery import Celery
from celery.signals import after_setup_task_logger
from celery.app.log import TaskFormatter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wms_local.settings')

app = Celery('wms_local')

CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['wms_local.celery_tasks.scheduled_tasks',
                        'wms_local.celery_tasks.background_tasks', ])


# FIXME: reformat celery task log to json format --> push log to ELK
@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter(
                '{"time":"%(asctime)s","task":"%(task_name)s","name":"%(name)s","messages": "%(message)s"'))
