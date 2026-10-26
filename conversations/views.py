from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationListSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Conversations.
    Supports: list, create, retrieve, update, delete.
    Extra actions: send_message, pin/unpin, clear_messages.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["agent", "is_pinned"]
    search_fields = ["title"]
    ordering_fields = ["updated_at", "created_at"]
    ordering = ["-updated_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ConversationListSerializer
        return ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user
        ).select_related("agent").prefetch_related("messages")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="send_message")
    def send_message(self, request, pk=None):
        """
        Send a user message to the conversation.
        Creates a Message record with role='user'.
        Agent response generation is handled asynchronously via Celery.
        """
        conversation = self.get_object()
        content = request.data.get("content", "").strip()
        if not content:
            return Response({"error": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

        user_message = Message.objects.create(
            conversation=conversation,
            role="user",
            content=content,
        )
        # Update conversation timestamp
        conversation.save(update_fields=["updated_at"])

        # TODO: Dispatch Celery task for agent response generation
        # from conversations.tasks import generate_agent_response
        # generate_agent_response.delay(conversation.id, user_message.id)

        serializer = MessageSerializer(user_message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="pin")
    def pin(self, request, pk=None):
        conversation = self.get_object()
        conversation.is_pinned = True
        conversation.save(update_fields=["is_pinned"])
        return Response({"is_pinned": True})

    @action(detail=True, methods=["post"], url_path="unpin")
    def unpin(self, request, pk=None):
        conversation = self.get_object()
        conversation.is_pinned = False
        conversation.save(update_fields=["is_pinned"])
        return Response({"is_pinned": False})

    @action(detail=True, methods=["delete"], url_path="clear_messages")
    def clear_messages(self, request, pk=None):
        conversation = self.get_object()
        conversation.messages.all().delete()
        return Response({"detail": "All messages cleared."}, status=status.HTTP_204_NO_CONTENT)
