from django.contrib import admin
from .models import Conversation, Message, MessageTemplate


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "service", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("sender__username", "receiver__username")
    raw_id_fields = ("sender", "receiver", "service", "last_message")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "conversation", "message_type", "is_read", "created_at")
    list_filter = ("message_type", "is_read", "created_at")
    search_fields = ("content", "sender__username")
    raw_id_fields = ("conversation", "sender")


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "shortcut", "created_at")
    search_fields = ("title", "content", "owner__username")
    raw_id_fields = ("owner",)
