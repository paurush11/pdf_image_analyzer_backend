import os
from celery import Celery, signals
from celery.schedules import crontab
from kombu import Queue, Exchange
import logging

logger = logging.getLogger(__name__)
"""
Exchanges & Queues (quick mental model)
    Exchange: where messages are published. Think “post office desk.”
    Queue: where messages wait to be consumed. Think “mailboxes.”
    Binding/routing_key: rule that connects an exchange to a queue.
You used a direct exchange and bound each queue with its own routing_key (same as the queue name).
That's perfect: tasks routed with routing_key="jobs" land in the jobs queue.
"""

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("pdf_image_analyzer_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.update(
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=30 * 60,
)
QUEUE_DEFAULT = os.getenv("CELERY_Q_DEFAULT", "default")
QUEUE_UPLOADS = os.getenv("CELERY_Q_UPLOADS", "file_upload")
QUEUE_JOBS = os.getenv("CELERY_Q_JOBS", "jobs")
QUEUE_ANALYTICS = os.getenv("CELERY_Q_ANALYTICS", "analytics")

default_ex = Exchange("celery", type="direct")
app.conf.task_default_queue = QUEUE_DEFAULT
app.conf.task_queues = (
    Queue(QUEUE_DEFAULT, default_ex, routing_key=QUEUE_DEFAULT),
    Queue(QUEUE_UPLOADS, default_ex, routing_key=QUEUE_UPLOADS),
    Queue(QUEUE_JOBS, default_ex, routing_key=QUEUE_JOBS),
    Queue(QUEUE_ANALYTICS, default_ex, routing_key=QUEUE_ANALYTICS),
)
app.conf.task_routes = {
    "apps.core_tasks.*": {"queue": QUEUE_DEFAULT, "routing_key": QUEUE_DEFAULT},
    "apps.file_upload_tasks.*": {"queue": QUEUE_UPLOADS, "routing_key": QUEUE_UPLOADS},
    "apps.jobs_tasks.*": {"queue": QUEUE_JOBS, "routing_key": QUEUE_JOBS},
    "apps.analytics_tasks.*": {
        "queue": QUEUE_ANALYTICS,
        "routing_key": QUEUE_ANALYTICS,
    },
}

# app.conf.beat_schedule = {
#     "feed-report-data-every-midnight": {
#         "task": "apps.analytics_tasks.tasks.feed_report_data",
#         "schedule": crontab(hour=0, minute=0),
#     },
# }


@signals.task_failure.connect
@signals.task_internal_error.connect
def task_failure_handler(**kwargs):
    sender = kwargs.get("sender")
    task_id = kwargs.get("task_id")
    exception = kwargs.get("exception")
    traceback = kwargs.get("traceback")
    exc_info = (type(exception), exception, traceback)

    logger.error(
        f"Task {sender} with ID {task_id} failed with exception: {exception}",
        exc_info=exc_info,
        extra={
            "data": {
                "task_id": task_id,
                "sender": sender,
                "exception": exception,
                "traceback": traceback,
            }
        },
    )


@signals.task_prerun.connect
def task_prerun_handler(task=None, task_id=None, **_):
    logger.info(f"Starting task {task.name} id={task_id}")


@signals.task_postrun.connect
def task_postrun_handler(task=None, task_id=None, state=None, **_):
    logger.info(f"Finished task {task.name} id={task_id} state={state}")
