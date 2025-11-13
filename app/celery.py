from celery import Celery
from .config import settings

# Create Celery instance
celery_app = Celery(
    "product_importer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['app.tasks']
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=1000,
    task_acks_late=True,  # Acknowledge tasks only after completion
    task_routes={
        'app.tasks.import_csv_task': {'queue': 'import_queue'},
        'app.tasks.send_webhook_task': {'queue': 'webhook_queue'},
    }
)