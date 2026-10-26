from rest_framework import serializers
from .models import Project, ProjectFile


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = [
            "id", "project", "file_path", "content", "language",
            "is_agent_generated", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectSerializer(serializers.ModelSerializer):
    files = ProjectFileSerializer(many=True, read_only=True)
    file_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "name", "description", "owner", "agent", "status",
            "primary_language", "tech_stack", "is_public",
            "file_count", "files", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_file_count(self, obj):
        return obj.files.count()


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no nested files)."""
    file_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "name", "description", "owner", "agent", "status",
            "primary_language", "tech_stack", "is_public",
            "file_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_file_count(self, obj):
        return obj.files.count()
