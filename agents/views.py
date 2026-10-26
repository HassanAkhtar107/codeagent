from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Agent, AgentSession, AgentLog
from .serializers import AgentSerializer, AgentSessionSerializer, AgentLogSerializer


class AgentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, and managing AI Agent configurations.
    """
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["provider", "status", "is_public"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Agent.objects.filter(
                models.Q(created_by=user) | models.Q(is_public=True)
            )
        return Agent.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        agent = self.get_object()
        agent.status = "active"
        agent.save(update_fields=["status"])
        return Response({"status": "activated"})

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        agent = self.get_object()
        agent.status = "inactive"
        agent.save(update_fields=["status"])
        return Response({"status": "deactivated"})


# Fix missing import
from django.db import models


class AgentSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Agent Sessions.
    """
    serializer_class = AgentSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["agent", "status"]
    ordering = ["-started_at"]

    def get_queryset(self):
        return AgentSession.objects.filter(user=self.request.user).select_related("agent")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"], url_path="logs")
    def logs(self, request, pk=None):
        session = self.get_object()
        logs = session.logs.all()
        serializer = AgentLogSerializer(logs, many=True)
        return Response(serializer.data)
