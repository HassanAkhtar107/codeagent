from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "code_agent_core.settings")

app = Celery("code_agent_core")
app.conf.enable_utc = True
app.conf.update(timezone=settings.TIME_ZONE)

app.conf.broker_transport_options = {'visibility_timeout': 7200}
app.config_from_object(settings, namespace="CELERY")


app.conf.beat_schedule = {
    # Daily database backup
    "database-backup": {
        "task": "users.tasks.databaseBackupDaily",
        "schedule": crontab(hour=5, minute=00),
    },
    # Periodic cleanup of expired agent sessions
    "cleanup-expired-sessions": {
        "task": "agents.tasks.cleanupExpiredSessions",
        "schedule": crontab(hour=3, minute=00),
    },
}

app.autodiscover_tasks()
