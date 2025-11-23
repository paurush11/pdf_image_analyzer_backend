"""Celery tasks for job operations."""
from celery import shared_task


@shared_task
def check_job_status(job_id):
    """Check job status from microservice."""
    # TODO: Implement job status checking task
    pass

