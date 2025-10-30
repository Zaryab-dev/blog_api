import os
from celery import Celery, signals
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leather_api.settings')

app = Celery('leather_api')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Task event handlers for monitoring
@signals.task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    logger.info(f'Task {task.name}[{task_id}] started')

@signals.task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, **kwargs):
    logger.info(f'Task {task.name}[{task_id}] completed')

@signals.task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    logger.error(f'Task {sender.name}[{task_id}] failed: {exception}')

@signals.task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, **kwargs):
    logger.warning(f'Task {sender.name}[{task_id}] retrying: {reason}')

# Periodic tasks
app.conf.beat_schedule = {
    'refresh-sitemap-daily': {
        'task': 'blog.tasks.regenerate_sitemap',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'refresh-rss-daily': {
        'task': 'blog.tasks.refresh_rss_feed',
        'schedule': crontab(hour=2, minute=30),  # 2:30 AM daily
    },
    'aggregate-metrics-daily': {
        'task': 'blog.tasks_analytics.aggregate_daily_metrics',
        'schedule': crontab(hour=1, minute=0),  # 1 AM daily
    },
    'export-trending-keywords': {
        'task': 'blog.tasks_analytics.export_trending_keywords',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
    'generate-openapi-schema': {
        'task': 'blog.tasks_docs.generate_openapi_schema',
        'schedule': crontab(hour=4, minute=0),  # 4 AM daily
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    logger.info(f'Request: {self.request!r}')
    return 'Debug task completed'
