"""
Conversations Models - نماذج المحادثات
نظام الرسائل المباشرة بين المستخدمين
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    """
    محادثة بين مستخدمين
    """

    class Meta:
        verbose_name = _("محادثة")
        verbose_name_plural = _("المحادثات")
        ordering = ["-updated_at"]
        unique_together = ["sender", "receiver"]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_conversations",
        verbose_name=_("المرسل"),
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_conversations",
        verbose_name=_("المستقبل"),
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
        verbose_name=_("الخدمة المرتبطة"),
    )
    last_message = models.ForeignKey(
        "Message",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations_as_last",
        verbose_name=_("آخر رسالة"),
    )
    sender_unread_count = models.PositiveIntegerField(
        default=0, verbose_name=_("رسائل غير مقروءة للمرسل")
    )
    receiver_unread_count = models.PositiveIntegerField(
        default=0, verbose_name=_("رسائل غير مقروءة للمستقبل")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    def __str__(self):
        return f"{self.sender.username} - {self.receiver.username}"

    def get_other_user(self, user):
        """الحصول على المستخدم الآخر في المحادثة"""
        if user == self.sender:
            return self.receiver
        return self.sender

    def mark_as_read(self, user):
        """تحديد الرسائل كمقروءة"""
        if user == self.sender:
            self.sender_unread_count = 0
        else:
            self.receiver_unread_count = 0
        self.save(
            update_fields=[
                "sender_unread_count"
                if user == self.sender
                else "receiver_unread_count"
            ]
        )
        Message.objects.filter(conversation=self, is_read=False).exclude(
            sender=user
        ).update(is_read=True)


class Message(models.Model):
    """
    رسالة في المحادثة
    """

    class MessageType(models.TextChoices):
        TEXT = "text", _("نص")
        IMAGE = "image", _("صورة")
        FILE = "file", _("ملف")
        SYSTEM = "system", _("نظام")

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("المحادثة"),
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name=_("المرسل"),
    )
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.TEXT,
        verbose_name=_("نوع الرسالة"),
    )
    content = models.TextField(verbose_name=_("المحتوى"))
    attachment = models.FileField(
        upload_to="conversations/attachments/",
        null=True,
        blank=True,
        verbose_name=_("المرفق"),
    )
    is_read = models.BooleanField(default=False, verbose_name=_("مقروء"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإرسال")
    )

    class Meta:
        verbose_name = _("رسالة")
        verbose_name_plural = _("الرسائل")
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            conversation = self.conversation
            conversation.last_message = self
            if self.sender == conversation.sender:
                conversation.receiver_unread_count += 1
            else:
                conversation.sender_unread_count += 1
            conversation.save(
                update_fields=[
                    "last_message",
                    "sender_unread_count"
                    if self.sender == conversation.sender
                    else "receiver_unread_count",
                    "updated_at",
                ]
            )


class MessageTemplate(models.Model):
    """
    قوالب الرسائل المحفوظة
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message_templates",
        verbose_name=_("المالك"),
    )
    title = models.CharField(max_length=100, verbose_name=_("عنوان القالب"))
    content = models.TextField(verbose_name=_("محتوى القالب"))
    shortcut = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("اختصار سريع للكتابة"),
        verbose_name=_("الاختصار"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )

    class Meta:
        verbose_name = _("قالب رسالة")
        verbose_name_plural = _("قوالب الرسائل")
        ordering = ["title"]

    def __str__(self):
        return self.title
