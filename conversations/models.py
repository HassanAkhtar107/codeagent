from django.db import models
from django.conf import settings

ROLE_CHOICES = (
    ("user", "User"),
    ("assistant", "Assistant"),
    ("system", "System"),
)


class Conversation(models.Model):
    """
    A conversation thread between a user and an AI agent.
    """
    title = models.CharField(max_length=255, blank=True, default="New Conversation")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
    )
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class Message(models.Model):
    """
    A single message within a conversation.
    Tracks role, content, token usage, and optional code/output blocks.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    content = models.TextField()
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    # Structured metadata (tool calls, citations, etc.)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.role}] {self.content[:80]}"
