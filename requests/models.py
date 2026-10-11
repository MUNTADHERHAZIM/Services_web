"""
Requests Models - نماذج طلبات الخدمات
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from services.models import Service
from django.utils import timezone
from core.validators import iraqi_phone_validator


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

    CANCELLATION_REASONS = [
        ('changed_mind', _('لم أعد بحاجة للخدمة حالياً (تغيير في الخطة)')),
        ('delay_provider', _('تأخر مقدم الخدمة في البدء أو التواصل')),
        ('order_mistake', _('تقديم الطلب بالخطأ أو تفاصيل غير مناسبة')),
        ('scope_disagreement', _('عدم الاتفاق على نطاق العمل أو شروط التنفيذ')),
        ('budget_issue', _('ظروف مالية خاصة أو تغيير في الميزانية المحددة')),
        ('found_alternative', _('العثور على بديل أو حل آخر مناسب')),
        ('other', _('سبب آخر (يرجى كتابة التوضيح أدناه)')),
    ]

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
    cancellation_reason = models.CharField(
        max_length=50,
        blank=True,
        choices=CANCELLATION_REASONS,
        verbose_name=_('سبب الإلغاء')
    )
    cancellation_notes = models.TextField(
        blank=True,
        verbose_name=_('تفاصيل وملاحظات الإلغاء')
    )
    canceled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الإلغاء')
    )
    canceled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='canceled_requests',
        verbose_name=_('تم الإلغاء بواسطة')
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[iraqi_phone_validator],
        verbose_name=_('رقم التواصل')
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name=_('البريد الإلكتروني')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('سعر الطلب النهائي')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('قيمة الخصم المطبق')
    )
    coupon = models.ForeignKey(
        'core.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('كوبون الخصم')
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

        # مزامنة وتحديث الوصل المالي للطلب
        try:
            from wallet.models import Receipt
            Receipt.create_or_get_for_request(self)
        except Exception:
            pass

    def cancel_order(self, reason, notes='', canceled_by=None, request=None):
        """تحديث حالة الطلب إلى ملغي مع تسجيل الأسباب وإشعار الإدارة ومقدم الخدمة"""
        from core.utils import log_action
        
        old_status = self.status
        self.status = self.Status.CANCELED
        self.cancellation_reason = reason
        self.cancellation_notes = notes
        self.canceled_at = timezone.now()
        self.canceled_by = canceled_by
        self.save(update_fields=[
            'status', 'cancellation_reason', 'cancellation_notes', 
            'canceled_at', 'canceled_by', 'updated_at'
        ])

        reason_display = dict(self.CANCELLATION_REASONS).get(reason, reason or 'غير محدد')
        notes_detail = f" - التفاصيل: {notes}" if notes else ""
        history_note = f"سبب الإلغاء: {reason_display}{notes_detail}"

        # 1. تسجيل تغيير الحالة
        StatusHistory.objects.create(
            request=self,
            from_status=old_status,
            to_status=self.Status.CANCELED,
            changed_by=canceled_by,
            notes=history_note
        )

        # 2. تحديث الوصل المالي للطلب
        try:
            from wallet.models import Receipt
            Receipt.create_or_get_for_request(self)
        except Exception:
            pass

        canceler_name = (canceled_by.get_full_name() or canceled_by.username) if canceled_by else self.customer.username

        # 2. إرسال إشعار فوري لجميع مدراء النظام والموظفين (Staff / Superusers)
        admin_users = User.objects.filter(is_staff=True)
        admin_title = f"⚠️ تم إلغاء الطلب #{self.pk}"
        admin_msg = (
            f"قام {canceler_name} بإلغاء الطلب #{self.pk} الخاص بالخدمة '{self.service.title}'.\n"
            f"السبب: {reason_display}\n"
            f"{notes_detail}"
        )
        for admin_user in admin_users:
            Notification.objects.create(
                user=admin_user,
                notification_type=Notification.NotificationType.REQUEST_CANCELED,
                title=admin_title,
                message=admin_msg,
                link=reverse('admin:requests_servicerequest_change', args=[self.pk])
            )

        # 3. إرسال إشعار لمقدم الخدمة إذا كان مختلفاً عن من ألغى الطلب
        try:
            provider_user = self.service.provider.user
            if provider_user and provider_user != canceled_by:
                Notification.objects.create(
                    user=provider_user,
                    notification_type=Notification.NotificationType.REQUEST_CANCELED,
                    title=f"تم إلغاء الطلب #{self.pk}",
                    message=(
                        f"نحيطك علماً بأن الطلب #{self.pk} للخدمة '{self.service.title}' قد تم إلغاؤه من قبل العميل.\n"
                        f"سبب الإلغاء: {reason_display}."
                    ),
                    link=self.get_absolute_url()
                )
        except Exception:
            pass

        # 4. تسجيل في سجل تدقيق الأمان AuditLog
        try:
            log_action(
                user=canceled_by,
                action_type='update',
                description=f"إلغاء الطلب #{self.pk} ({self.service.title}) - السبب: {reason_display}",
                request=request
            )
        except Exception:
            pass


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
        REQUEST_CANCELED = 'request_canceled', _('إلغاء الطلب')
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
