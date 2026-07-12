from celery import Celery

from src.core.config import CELERY_BROKER_URL

app = Celery(
    "src.celery.celery_app",
    broker=CELERY_BROKER_URL,
    broker_connection_retry_on_startup=True,
)
app.autodiscover_tasks(["src.celery.tasks"])
