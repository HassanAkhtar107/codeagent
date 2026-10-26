from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Project, ProjectFile
from .serializers import (
    ProjectSerializer, ProjectListSerializer,
    ProjectFileSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing coding Projects.
    Extra actions: archive, activate, add_file, list_files.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "primary_language", "is_public"]
    search_fields = ["name", "description"]
    ordering_fields = ["updated_at", "created_at", "name"]
    ordering = ["-updated_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(
            owner=self.request.user
        ).select_related("agent").prefetch_related("files")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        project = self.get_object()
        project.status = "archived"
        project.save(update_fields=["status"])
        return Response({"status": "archived"})

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        project = self.get_object()
        project.status = "active"
        project.save(update_fields=["status"])
        return Response({"status": "active"})

    @action(detail=True, methods=["get"], url_path="files")
    def list_files(self, request, pk=None):
        project = self.get_object()
        files = project.files.all()
        serializer = ProjectFileSerializer(files, many=True)
        return Response(serializer.data)


class ProjectFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual files within Projects.
    """
    serializer_class = ProjectFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["project", "language", "is_agent_generated"]
    search_fields = ["file_path"]

    def get_queryset(self):
        return ProjectFile.objects.filter(
            project__owner=self.request.user
        ).select_related("project")
