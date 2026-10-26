from django.db import models
from django.conf import settings

PROJECT_STATUS_CHOICES = (
    ("active", "Active"),
    ("archived", "Archived"),
    ("draft", "Draft"),
)


class Project(models.Model):
    """
    A coding project workspace managed by the Code Agent platform.
    Can be linked to a specific agent for AI-assisted development.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    status = models.CharField(choices=PROJECT_STATUS_CHOICES, max_length=10, default="active")
    primary_language = models.CharField(max_length=50, default="python")
    tech_stack = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class ProjectFile(models.Model):
    """
    A file within a coding project.
    Stores the file path, content, and tracks agent-generated diffs.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="files",
    )
    file_path = models.CharField(max_length=500)
    content = models.TextField(blank=True, default="")
    language = models.CharField(max_length=50, blank=True, null=True)
    is_agent_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["file_path"]
        unique_together = [("project", "file_path")]

    def __str__(self):
        return f"{self.project.name} / {self.file_path}"
