from django.contrib import admin
from .models import Agent, AgentSession, AgentLog


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["name", "provider", "model_name", "status", "is_public", "created_by", "created_at"]
    list_filter = ["provider", "status", "is_public"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(AgentSession)
class AgentSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "agent", "user", "status", "total_input_tokens", "total_output_tokens", "started_at"]
    list_filter = ["status", "agent"]
    readonly_fields = ["started_at", "ended_at"]


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = ["id", "session", "level", "message", "created_at"]
    list_filter = ["level"]
    readonly_fields = ["created_at"]
