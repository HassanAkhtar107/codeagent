from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["created_at", "input_tokens", "output_tokens"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "user", "agent", "is_pinned", "created_at", "updated_at"]
    list_filter = ["is_pinned", "agent"]
    search_fields = ["title", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "conversation", "role", "content_preview", "input_tokens", "output_tokens", "created_at"]
    list_filter = ["role"]
    readonly_fields = ["created_at"]

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = "Content"
