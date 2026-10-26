from rest_framework import serializers
from .models import CodeRun


class CodeRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeRun
        fields = [
            "id", "user", "language", "source_code", "stdin",
            "stdout", "stderr", "exit_code", "status", "duration_ms", "created_at",
        ]
        read_only_fields = ["id", "user", "stdout", "stderr", "exit_code", "status", "duration_ms", "created_at"]


class CodeRunRequestSerializer(serializers.Serializer):
    """Serializer for the /api/executor/run/ endpoint request body."""
    language = serializers.ChoiceField(choices=["python", "javascript", "bash", "typescript", "sql"])
    source_code = serializers.CharField()
    stdin = serializers.CharField(required=False, default="", allow_blank=True)
