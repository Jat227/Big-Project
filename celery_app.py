from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "pricefinder",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    # Retry failed tasks up to 3 times
    task_max_retries=3,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
