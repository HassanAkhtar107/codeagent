from rest_framework import serializers
from .models import Agent, AgentSession, AgentLog


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            "id", "name", "description", "provider", "model_name",
            "system_prompt", "temperature", "max_tokens", "status",
            "is_public", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class AgentSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentSession
        fields = [
            "id", "agent", "user", "status",
            "total_input_tokens", "total_output_tokens",
            "started_at", "ended_at",
        ]
        read_only_fields = ["id", "user", "started_at", "ended_at"]


class AgentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentLog
        fields = ["id", "session", "level", "message", "metadata", "created_at"]
        read_only_fields = ["id", "created_at"]
