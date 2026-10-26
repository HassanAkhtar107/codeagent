from django.db import models
from django.conf import settings

LANGUAGE_CHOICES = (
    ("python", "Python"),
    ("javascript", "JavaScript"),
    ("bash", "Bash"),
    ("typescript", "TypeScript"),
    ("sql", "SQL"),
)

RUN_STATUS_CHOICES = (
    ("pending", "Pending"),
    ("running", "Running"),
    ("success", "Success"),
    ("error", "Error"),
    ("timeout", "Timeout"),
)


class CodeRun(models.Model):
    """
    A record of a code snippet execution in the sandbox.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="code_runs",
    )
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=20, default="python")
    source_code = models.TextField()
    stdin = models.TextField(blank=True, default="")
    stdout = models.TextField(blank=True, default="")
    stderr = models.TextField(blank=True, default="")
    exit_code = models.IntegerField(null=True, blank=True)
    status = models.CharField(choices=RUN_STATUS_CHOICES, max_length=10, default="pending")
    duration_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"CodeRun #{self.id} [{self.language}] — {self.status}"
