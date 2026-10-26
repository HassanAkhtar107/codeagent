from django.db import models
from django.conf import settings

PROVIDER_CHOICES = (
    ("openai", "OpenAI"),
    ("anthropic", "Anthropic"),
    ("gemini", "Google Gemini"),
    ("custom", "Custom"),
)

STATUS_CHOICES = (
    ("active", "Active"),
    ("inactive", "Inactive"),
)

SESSION_STATUS_CHOICES = (
    ("running", "Running"),
    ("completed", "Completed"),
    ("failed", "Failed"),
    ("expired", "Expired"),
)


class Agent(models.Model):
    """
    An AI Agent configuration.
    Each agent has a provider, model, system prompt, and optional tools.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    provider = models.CharField(choices=PROVIDER_CHOICES, max_length=20, default="openai")
    model_name = models.CharField(max_length=100, default="gpt-4o")
    system_prompt = models.TextField(blank=True, default="You are a helpful AI coding assistant.")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=4096)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default="active")
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.provider}/{self.model_name})"


class AgentSession(models.Model):
    """
    A single execution session for an agent.
    Tracks the session lifecycle and cumulative token usage.
    """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="sessions")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agent_sessions",
    )
    status = models.CharField(choices=SESSION_STATUS_CHOICES, max_length=20, default="running")
    total_input_tokens = models.IntegerField(default=0)
    total_output_tokens = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Session {self.id} — {self.agent.name} [{self.status}]"


class AgentLog(models.Model):
    """
    A log entry for an agent session step (tool call, message, error, etc.)
    """
    LOG_LEVELS = (
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("debug", "Debug"),
    )
    session = models.ForeignKey(AgentSession, on_delete=models.CASCADE, related_name="logs")
    level = models.CharField(choices=LOG_LEVELS, max_length=10, default="info")
    message = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.level.upper()}] {self.session} — {self.message[:80]}"
