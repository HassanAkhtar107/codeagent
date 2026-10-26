from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def cleanupExpiredSessions():
    """
    Periodic Celery task: mark sessions older than 24 hours with status
    'running' as 'expired' and close them out.
    """
    from .models import AgentSession

    expiry_threshold = timezone.now() - timedelta(hours=24)
    expired = AgentSession.objects.filter(
        status="running",
        started_at__lt=expiry_threshold,
    )
    count = expired.update(status="expired", ended_at=timezone.now())
    return f"Expired {count} stale agent sessions."
