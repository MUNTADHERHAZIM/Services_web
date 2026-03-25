"""
Requests Models - نماذج طلبات الخدمات
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from services.models import Service


class ServiceRequest(models.Model):
    """
    طلب خدمة
    """
    class Status(models.TextChoices):
        NEW = 'new', _('جديد')
        IN_REVIEW = 'in_review', _('قيد المراجعة')
        APPROVED = 'approved', _('تمت الموافقة')
        REJECTED = 'rejected', _('مرفوض')
        IN_PROGRESS = 'in_progress', _('قيد التنفيذ')
        DONE = 'done', _('مكتمل')
        CANCELED = 'canceled', _('ملغي')

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name=_('الخدمة')
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='service_requests',
        verbose_name=_('العميل')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_('الحالة')
    )
    customer_notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات العميل')
    )
    staff_notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات الموظف')
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('رقم التواصل')
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name=_('البريد الإلكتروني')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )

    class Meta:
        verbose_name = _('طلب خدمة')
        verbose_name_plural = _('طلبات الخدمات')
        ordering = ['-created_at']
        permissions = [
            ('can_manage_requests', 'يمكنه إدارة الطلبات'),
            ('can_change_status', 'يمكنه تغيير حالة الطلب'),
        ]

    def __str__(self):
        return f"طلب #{self.pk} - {self.service.title}"

    def get_absolute_url(self):
        return reverse('requests:request_detail', kwargs={'pk': self.pk})

    def get_status_badge_class(self):
        """إرجاع كلاس Bootstrap للحالة"""
        status_classes = {
            'new': 'bg-primary',
            'in_review': 'bg-info',
            'approved': 'bg-success',
            'rejected': 'bg-danger',
            'in_progress': 'bg-warning text-dark',
            'done': 'bg-success',
            'canceled': 'bg-secondary',
        }
        return status_classes.get(self.status, 'bg-secondary')

    def can_be_canceled(self):
        """هل يمكن إلغاء الطلب؟"""
        return self.status in ['new', 'in_review', 'approved']

    def update_status(self, new_status, changed_by, notes=''):
        """تحديث حالة الطلب مع تسجيل التغيير"""
        old_status = self.status
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
        
        # تسجيل تغيير الحالة
        StatusHistory.objects.create(
            request=self,
            from_status=old_status,
            to_status=new_status,
            changed_by=changed_by,
            notes=notes
        )


class StatusHistory(models.Model):
    """
    سجل تغييرات حالة الطلب
    """
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('الطلب')
    )
    from_status = models.CharField(
        max_length=20,
        choices=ServiceRequest.Status.choices,
        verbose_name=_('من حالة')
    )
    to_status = models.CharField(
        max_length=20,
        choices=ServiceRequest.Status.choices,
        verbose_name=_('إلى حالة')
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes',
        verbose_name=_('تم التغيير بواسطة')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ التغيير')
    )

    class Meta:
        verbose_name = _('سجل تغيير الحالة')
        verbose_name_plural = _('سجلات تغييرات الحالات')
        ordering = ['-created_at']

    def __str__(self):
        return f"تغيير طلب #{self.request.pk}: {self.get_from_status_display()} → {self.get_to_status_display()}"


class Notification(models.Model):
    """
    إشعارات النظام
    """
    class NotificationType(models.TextChoices):
        REQUEST_NEW = 'request_new', _('طلب جديد')
        REQUEST_STATUS = 'request_status', _('تحديث حالة الطلب')
        REQUEST_COMMENT = 'request_comment', _('تعليق جديد')
        SYSTEM = 'system', _('إشعار النظام')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('المستخدم')
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        verbose_name=_('نوع الإشعار')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('العنوان')
    )
    message = models.TextField(
        verbose_name=_('الرسالة')
    )
    link = models.URLField(
        blank=True,
        verbose_name=_('الرابط')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('مقروء')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )

    class Meta:
        verbose_name = _('إشعار')
        verbose_name_plural = _('الإشعارات')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def mark_as_read(self):
        """تحديد الإشعار كمقروء"""
        self.is_read = True
        self.save(update_fields=['is_read'])
