from __future__ import annotations

import os
from datetime import timedelta

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")


app = Celery(
    "mysite",
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/1",
    broker_connection_retry_on_startup=True,
    include=["mysite.celery_tasks"],
)


app.conf.update(
    timezone="Europe/Warsaw",
    enable_utc=True,
    beat_schedule={
        "website-availability-task": {
            "task": "mysite.celery_tasks.check_website_availability",
            "schedule": timedelta(seconds=10),
            # 'schedule': crontab(hour=0, minute=0),  # Każdej nocy o północy
            # 'args': (("data11",)),
        },
    },
)


# Using a string here means the worker doesn't have to serialize the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


# Tasks autodetection for module celery_tasks:
app.autodiscover_tasks(["mysite.celery_tasks"])
