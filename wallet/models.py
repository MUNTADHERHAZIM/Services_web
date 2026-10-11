import hashlib
import io
import uuid
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse


class Wallet(models.Model):
    """
    محفظة المستخدم
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
        verbose_name=_("المستخدم"),
    )
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name=_("الرصيد")
    )
    frozen_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name=_("الرصيد المجمد")
    )
    total_earned = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name=_("إجمالي الأرباح")
    )
    total_withdrawn = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name=_("إجمالي السحوبات")
    )
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("العملة"))
    is_active = models.BooleanField(default=True, verbose_name=_("نشط"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("محفظة")
        verbose_name_plural = _("المحافظ")

    def __str__(self):
        return f"{self.user.username} - {self.balance}"

    @property
    def available_balance(self):
        return max(0, self.balance - self.frozen_balance)


class DepositMethod(models.Model):
    """
    وسائل الدفع وشحن الرصيد المعتمدة في المنصة (قابلة للإدارة من الأدمن)
    """
    name = models.CharField(
        max_length=100, 
        verbose_name=_("اسم وسيلة الدفع / المحفظة")
    )
    account_name = models.CharField(
        max_length=150, 
        verbose_name=_("اسم صاحب الحساب / المستلم")
    )
    account_number = models.CharField(
        max_length=120, 
        verbose_name=_("رقم الحساب / المحفظة / IBAN")
    )
    instructions = models.TextField(
        blank=True, 
        verbose_name=_("تعليمات التحويل للعميل")
    )
    min_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=5.00, 
        verbose_name=_("الحد الأدنى للشحن ($)")
    )
    max_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=5000.00, 
        verbose_name=_("الحد الأقصى للشحن ($)")
    )
    icon_class = models.CharField(
        max_length=50, 
        default="bi-phone", 
        verbose_name=_("أيقونة الوسيلة (Bootstrap Icons)")
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name=_("مفعلة")
    )
    display_order = models.PositiveIntegerField(
        default=0, 
        verbose_name=_("ترتيب العرض")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("تاريخ الإنشاء")
    )

    class Meta:
        verbose_name = _("وسيلة دفع وشحن")
        verbose_name_plural = _("وسائل الدفع والشحن")
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.name} - {self.account_number}"


class DepositRequest(models.Model):
    """
    طلبات شحن الرصيد بإشعار التحويل اليدوي (تنتظر موافقة وتدقيق السوبر أدمن)
    """
    class Status(models.TextChoices):
        PENDING = "pending", _("قيد المراجعة والتدقيق")
        APPROVED = "approved", _("تمت الموافقة وشحن الرصيد")
        REJECTED = "rejected", _("مرفوض")

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="deposit_requests",
        verbose_name=_("المحفظة")
    )
    deposit_method = models.ForeignKey(
        DepositMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deposit_requests",
        verbose_name=_("وسيلة الدفع")
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("المبلغ المطلوب شحنه ($)")
    )
    sender_name = models.CharField(
        max_length=150,
        verbose_name=_("اسم صاحب الحساب المحوِّل")
    )
    sender_phone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("رقم هاتف المحوّل / الحساب")
    )
    transaction_reference = models.CharField(
        max_length=120,
        verbose_name=_("رقم الحوالة / الإشعار المرجعي")
    )
    receipt_image = models.ImageField(
        upload_to="deposit_receipts/%Y/%m/",
        verbose_name=_("صورة وصل أو إشعار التحويل")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("حالة الطلب")
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name=_("ملاحظات الإدارة / سبب الرفض")
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_deposits",
        verbose_name=_("تمت المراجعة بواسطة")
    )
    reference_id = models.CharField(
        max_length=60,
        unique=True,
        verbose_name=_("رمز الطلب المرجعي")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الطلب")
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ المراجعة")
    )

    class Meta:
        verbose_name = _("طلب شحن رصيد")
        verbose_name_plural = _("طلبات شحن الرصيد")
        ordering = ["-created_at"]

    def __str__(self):
        return f"طلب #{self.reference_id} - {self.wallet.user.username} (${self.amount})"

    def approve(self, admin_user=None, admin_notes="", request=None):
        """الموافقة على طلب الشحن وإضافة الرصيد للمحفظة فوراً بشكل ذري آمن"""
        from django.db import transaction as db_transaction
        from core.utils import log_action
        from requests.models import Notification

        if self.status != self.Status.PENDING:
            raise ValueError("لا يمكن الموافقة على طلب تمت معالجته مسبقاً.")

        with db_transaction.atomic():
            # قفل المحفظة لمنع التضارب
            wallet = Wallet.objects.select_for_update().get(pk=self.wallet_id)
            wallet.balance += self.amount
            wallet.save(update_fields=['balance', 'updated_at'])

            # تسجيل المعاملة المالية المكتملة
            method_name = self.deposit_method.name if self.deposit_method else "تحويل يدوي"
            Transaction.objects.create(
                wallet=wallet,
                transaction_type=Transaction.TransactionType.DEPOSIT,
                amount=self.amount,
                status=Transaction.TransactionStatus.COMPLETED,
                description=f"شحن رصيد معتمد عبر {method_name} - إشعار #{self.transaction_reference}",
                reference_id=self.reference_id,
                completed_at=timezone.now()
            )

            # تحديث حالة الطلب
            self.status = self.Status.APPROVED
            self.reviewed_by = admin_user
            if admin_notes:
                self.admin_notes = admin_notes
            self.reviewed_at = timezone.now()
            self.save(update_fields=['status', 'reviewed_by', 'admin_notes', 'reviewed_at'])

            # تحديث أي معاملة قيد الانتظار بهذا المرجع إن وجدت
            Transaction.objects.filter(
                wallet=wallet,
                reference_id=self.reference_id,
                status=Transaction.TransactionStatus.PENDING
            ).update(status=Transaction.TransactionStatus.COMPLETED, completed_at=timezone.now())

            # إنشاء وتحديث الوصل المالي المعتمد
            try:
                Receipt.create_or_get_for_deposit(self)
            except Exception:
                pass

            # إشعار المستخدم
            try:
                Notification.objects.create(
                    user=wallet.user,
                    notification_type=Notification.NotificationType.SYSTEM,
                    title="🎉 تم شحن رصيدك بنجاح!",
                    message=f"تمت مراجعة حوالتك والتأكد من استلام المبلغ (${self.amount}). تمت إضافة الرصيد إلى محفظتك بنجاح وهو متاح للاستخدام الآن.",
                    link="/wallet/"
                )
            except Exception:
                pass

            # تسجيل الحركة في سجل التدقيق
            try:
                log_action(
                    user=admin_user or wallet.user,
                    action_type='wallet',
                    description=f"موافقة على طلب شحن الرصيد #{self.reference_id} بمبلغ ${self.amount} للمستخدم {wallet.user.username}",
                    request=request
                )
            except Exception:
                pass

    def reject(self, admin_user=None, admin_notes="", request=None):
        """رفض طلب الشحن مع توضيح السبب وإشعار المستخدم دون المساس بالأرصدة"""
        from django.db import transaction as db_transaction
        from core.utils import log_action
        from requests.models import Notification

        if self.status != self.Status.PENDING:
            raise ValueError("لا يمكن رفض طلب تمت معالجته مسبقاً.")

        with db_transaction.atomic():
            self.status = self.Status.REJECTED
            self.reviewed_by = admin_user
            self.admin_notes = admin_notes or "تعذر تأكيد استلام الحوالة من قبل الإدارة."
            self.reviewed_at = timezone.now()
            self.save(update_fields=['status', 'reviewed_by', 'admin_notes', 'reviewed_at'])

            # إلغاء المعاملة المعلقة إن وجدت
            Transaction.objects.filter(
                wallet=self.wallet,
                reference_id=self.reference_id,
                status=Transaction.TransactionStatus.PENDING
            ).update(status=Transaction.TransactionStatus.CANCELED)

            # تحديث الوصل المالي بالحالة الجديدة
            try:
                Receipt.create_or_get_for_deposit(self)
            except Exception:
                pass

            # إشعار المستخدم بالرفض
            try:
                Notification.objects.create(
                    user=self.wallet.user,
                    notification_type=Notification.NotificationType.SYSTEM,
                    title="تنبيه: تم رفض طلب شحن الرصيد",
                    message=f"نأسف لإبلاغك بأنه تم رفض طلب شحن الرصيد بمبلغ (${self.amount}). السبب: {self.admin_notes}",
                    link="/wallet/"
                )
            except Exception:
                pass

            # تسجيل الحركة في سجل التدقيق
            try:
                log_action(
                    user=admin_user or self.wallet.user,
                    action_type='wallet',
                    description=f"رفض طلب شحن الرصيد #{self.reference_id} بمبلغ ${self.amount} للمستخدم {self.wallet.user.username} - السبب: {self.admin_notes}",
                    request=request
                )
            except Exception:
                pass


class Transaction(models.Model):
    """
    المعاملات المالية
    """

    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", _("إيداع")
        WITHDRAWAL = "withdrawal", _("سحب")
        ORDER_PAYMENT = "order_payment", _("دفع طلب")
        ORDER_EARNING = "order_earning", _("أرباح طلب")
        REFUND = "refund", _("استرداد")
        FEE = "fee", _("رسوم")
        BONUS = "bonus", _("مكافأة")
        TRANSFER = "transfer", _("تحويل")

    class TransactionStatus(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار")
        COMPLETED = "completed", _("مكتمل")
        FAILED = "failed", _("فشل")
        CANCELED = "canceled", _("ملغي")

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name=_("المحفظة"),
    )
    transaction_type = models.CharField(
        max_length=20, choices=TransactionType.choices, verbose_name=_("نوع المعاملة")
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("المبلغ")
    )
    fee = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name=_("الرسوم")
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        verbose_name=_("الحالة"),
    )
    description = models.TextField(blank=True, verbose_name=_("الوصف"))
    reference_id = models.CharField(
        max_length=100, blank=True, verbose_name=_("رقم المرجع")
    )
    related_order = models.ForeignKey(
        "requests.ServiceRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name=_("الطلب المرتبط"),
    )
    metadata = models.JSONField(
        default=dict, blank=True, verbose_name=_("بيانات إضافية")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ المعاملة")
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاريخ الإتمام")
    )

    class Meta:
        verbose_name = _("معاملة")
        verbose_name_plural = _("المعاملات")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - {self.amount}"

    def save(self, *args, **kwargs):
        if self.status == self.TransactionStatus.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class WithdrawalRequest(models.Model):
    """
    طلبات السحب
    """

    class WithdrawalMethod(models.TextChoices):
        ZAIN_CASH = "zain_cash", _("زين كاش (ZainCash)")
        QI_CARD = "qi_card", _("كي كارد / مصرف الرافدين (Qi Card)")
        WESTERN_UNION = "western_union", _("ويسترن يونيون (Western Union)")
        BANK_TRANSFER = "bank", _("تحويل بنكي مباشر (IBAN)")
        WISE = "wise", _("منصة وايز (Wise)")
        OTHER = "other", _("وسيلة أخرى")

    class Status(models.TextChoices):
        PENDING = "pending", _("قيد الانتظار")
        PROCESSING = "processing", _("قيد المعالجة")
        COMPLETED = "completed", _("مكتمل")
        REJECTED = "rejected", _("مرفوض")

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="withdrawal_requests",
        verbose_name=_("المحفظة"),
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("المبلغ")
    )
    method = models.CharField(
        max_length=30, choices=WithdrawalMethod.choices, verbose_name=_("طريقة السحب")
    )
    account_info = models.JSONField(verbose_name=_("معلومات الحساب"))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("الحالة"),
    )
    admin_notes = models.TextField(blank=True, verbose_name=_("ملاحظات المسؤول"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الطلب"))
    processed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("تاريخ المعالجة")
    )

    class Meta:
        verbose_name = _("طلب سحب")
        verbose_name_plural = _("طلبات السحب")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.wallet.user.username} - {self.amount}"

    def approve(self, admin_user=None, admin_notes="", request=None):
        """الموافقة على طلب السحب بعد إرسال الحوالة الفعلية للعميل"""
        from django.db import transaction as db_transaction
        from core.utils import log_action
        from requests.models import Notification

        if self.status not in [self.Status.PENDING, self.Status.PROCESSING]:
            raise ValueError("لا يمكن الموافقة على طلب تم البت فيه مسبقاً.")

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.wallet_id)
            wallet.frozen_balance = max(0, wallet.frozen_balance - self.amount)
            wallet.balance = max(0, wallet.balance - self.amount)
            wallet.total_withdrawn += self.amount
            wallet.save(update_fields=['balance', 'frozen_balance', 'total_withdrawn', 'updated_at'])

            self.status = self.Status.COMPLETED
            if admin_notes:
                self.admin_notes = admin_notes
            self.processed_at = timezone.now()
            self.save(update_fields=['status', 'admin_notes', 'processed_at'])

            Transaction.objects.create(
                wallet=wallet,
                transaction_type=Transaction.TransactionType.WITHDRAWAL,
                amount=self.amount,
                status=Transaction.TransactionStatus.COMPLETED,
                description=f"تم تحويل وسحب الرصيد بنجاح إلى {self.get_method_display()}",
                completed_at=timezone.now()
            )

            # إنشاء وتحديث سند ووصل السحب الرسمي
            try:
                Receipt.create_or_get_for_withdrawal(self)
            except Exception:
                pass

            try:
                Notification.objects.create(
                    user=wallet.user,
                    notification_type=Notification.NotificationType.SYSTEM,
                    title="تم تحويل أرباحك بنجاح! 💸",
                    message=f"تمت معالجة طلب سحب الرصيد بمبلغ (${self.amount}) وإرسال المبلغ بنجاح عبر {self.get_method_display()}.",
                    link="/wallet/"
                )
            except Exception:
                pass

            try:
                log_action(
                    user=admin_user or wallet.user,
                    action_type='wallet',
                    description=f"موافقة على سحب رصيد بمبلغ ${self.amount} للمستخدم {wallet.user.username}",
                    request=request
                )
            except Exception:
                pass

    def reject(self, admin_user=None, admin_notes="", request=None):
        """رفض طلب السحب وإلغاء تجميد المبلغ ليعود متاحاً في المحفظة"""
        from django.db import transaction as db_transaction
        from core.utils import log_action
        from requests.models import Notification

        if self.status not in [self.Status.PENDING, self.Status.PROCESSING]:
            raise ValueError("لا يمكن رفض طلب تم البت فيه مسبقاً.")

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.wallet_id)
            wallet.frozen_balance = max(0, wallet.frozen_balance - self.amount)
            wallet.save(update_fields=['frozen_balance', 'updated_at'])

            self.status = self.Status.REJECTED
            self.admin_notes = admin_notes or "تم رفض طلب السحب من قبل الإدارة."
            self.processed_at = timezone.now()
            self.save(update_fields=['status', 'admin_notes', 'processed_at'])

            Transaction.objects.filter(
                wallet=wallet,
                transaction_type=Transaction.TransactionType.WITHDRAWAL,
                status=Transaction.TransactionStatus.PENDING
            ).update(status=Transaction.TransactionStatus.CANCELED)

            # تحديث سند السحب بالحالة الجديدة
            try:
                Receipt.create_or_get_for_withdrawal(self)
            except Exception:
                pass

            try:
                Notification.objects.create(
                    user=wallet.user,
                    notification_type=Notification.NotificationType.SYSTEM,
                    title="تنبيه: تم رفض طلب سحب الرصيد",
                    message=f"تم رفض طلب السحب بمبلغ (${self.amount}) وتمت إعادة المبلغ لمحفظتك. السبب: {self.admin_notes}",
                    link="/wallet/"
                )
            except Exception:
                pass

            try:
                log_action(
                    user=admin_user or wallet.user,
                    action_type='wallet',
                    description=f"رفض طلب سحب رصيد بمبلغ ${self.amount} للمستخدم {wallet.user.username} - السبب: {self.admin_notes}",
                    request=request
                )
            except Exception:
                pass


class Receipt(models.Model):
    """
    نموذج الوصل والفاتورة المالية المعتمدة في النظام
    يوثق ويحفظ كل العمليات المالية:
    1. وصولات وفواتير طلبات الخدمات (Service Orders)
    2. وصولات شحن الرصيد المالي وإشعارات التحويل (Deposits)
    3. وصولات وسندات سحب الأرباح والحوالات (Withdrawals)
    4. وصولات استرداد الأموال والتحويل بين المحافظ (Refunds & Transfers)
    يتضمن QR كود للتحقق الرقمي المباشر، وتشفير البصمة SHA-256، وحفظ تفاصيل العملية بدقة
    """

    class ReceiptType(models.TextChoices):
        ORDER = "order", _("فاتورة طلب خدمة")
        DEPOSIT = "deposit", _("وصل إيداع وشحن رصيد")
        WITHDRAWAL = "withdrawal", _("سند سحب أرباح ورصيد")
        REFUND = "refund", _("وصل استرداد مالي")
        TRANSFER = "transfer", _("وصل تحويل رصيد")
        GENERAL = "general", _("وصل معاملة مالية")

    class Status(models.TextChoices):
        COMPLETED = "completed", _("معتمد ومكتمل")
        PENDING = "pending", _("قيد المعالجة والتدقيق")
        CANCELLED = "cancelled", _("ملغي / مسترد")

    receipt_number = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name=_("رقم الوصل / الفاتورة")
    )
    receipt_type = models.CharField(
        max_length=20,
        choices=ReceiptType.choices,
        default=ReceiptType.GENERAL,
        db_index=True,
        verbose_name=_("نوع الوصل")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
        db_index=True,
        verbose_name=_("حالة الوصل")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="receipts",
        verbose_name=_("العميل / صاحب الحساب")
    )
    counterpart_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="counterpart_receipts",
        verbose_name=_("الطرف الثاني (مقدم الخدمة / المستلم)")
    )
    service_request = models.ForeignKey(
        "requests.ServiceRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipts",
        verbose_name=_("الطلب المرتبط")
    )
    deposit_request = models.ForeignKey(
        "wallet.DepositRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipts",
        verbose_name=_("طلب الشحن المرتبط")
    )
    withdrawal_request = models.ForeignKey(
        "wallet.WithdrawalRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipts",
        verbose_name=_("طلب السحب المرتبط")
    )
    transaction = models.ForeignKey(
        "wallet.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receipts",
        verbose_name=_("المعاملة المالية")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان المعاملة أو الخدمة")
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("المبلغ الأساسي ($)")
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("قيمة الخصم ($)")
    )
    tax_or_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("الرسوم / الضرائب ($)")
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("المبلغ الإجمالي الصافي ($)")
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
        verbose_name=_("العملة الأساسية")
    )
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1500.00"),
        verbose_name=_("سعر الصرف المعتمد")
    )
    amount_iqd = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("المبلغ المعادل بالدينار العراقي (د.ع)")
    )
    payment_method_name = models.CharField(
        max_length=150,
        default="محفظة خدماتي الإلكترونية",
        verbose_name=_("وسيلة الدفع / التحويل")
    )
    payment_reference = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("المرجع / كود الحوالة")
    )
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name=_("رمز التحقق الرقمي")
    )
    qr_code_svg = models.TextField(
        blank=True,
        verbose_name=_("كود الاستجابة السريع (SVG)")
    )
    security_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_("البصمة الرقمية المشفرة (SHA-256)")
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("بيانات وتفاصيل إضافية")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("ملاحظات وشروط الضمان")
    )
    issued_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("تاريخ ووقت الإصدار")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )

    class Meta:
        verbose_name = _("وصل مالي رسمي")
        verbose_name_plural = _("الوصولات والفواتير الرسمية")
        ordering = ["-issued_at", "-id"]

    def __str__(self):
        return f"{self.receipt_number} - {self.title} (${self.total_amount})"

    def get_absolute_url(self):
        return reverse("wallet:receipt_detail", kwargs={"receipt_number": self.receipt_number})

    def get_verification_url(self, request=None):
        verify_path = reverse("wallet:receipt_verify", kwargs={"token": self.verification_token})
        if request:
            return request.build_absolute_uri(verify_path)
        return verify_path

    def get_badge_class(self):
        mapping = {
            self.Status.COMPLETED: "bg-success",
            self.Status.PENDING: "bg-warning text-dark",
            self.Status.CANCELLED: "bg-danger",
        }
        return mapping.get(self.status, "bg-secondary")

    def generate_qr_code_svg(self, base_url=""):
        try:
            import qrcode
            import qrcode.image.svg
            verify_path = f"/wallet/receipt/verify/{self.verification_token}/"
            full_url = f"{base_url.rstrip('/')}{verify_path}" if base_url else verify_path
            factory = qrcode.image.svg.SvgPathImage
            img = qrcode.make(full_url, image_factory=factory, box_size=8, border=1)
            stream = io.BytesIO()
            img.save(stream)
            return stream.getvalue().decode("utf-8")
        except Exception:
            return ""

    def save(self, *args, **kwargs):
        if self.total_amount is not None and not self.amount_iqd:
            self.amount_iqd = Decimal(str(self.total_amount)) * Decimal(str(self.exchange_rate or 1500))

        if not self.security_hash:
            data_to_hash = f"{self.receipt_number}:{self.user_id}:{self.total_amount}:{self.issued_at.strftime('%Y%m%d%H%M%S')}"
            self.security_hash = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()

        if not self.qr_code_svg:
            self.qr_code_svg = self.generate_qr_code_svg()

        super().save(*args, **kwargs)

    @classmethod
    def create_or_get_for_request(cls, service_request, base_url=""):
        receipt = cls.objects.filter(service_request=service_request).first()
        status_map = {
            'approved': cls.Status.COMPLETED,
            'in_progress': cls.Status.COMPLETED,
            'done': cls.Status.COMPLETED,
            'canceled': cls.Status.CANCELLED,
            'rejected': cls.Status.CANCELLED,
            'new': cls.Status.PENDING,
            'in_review': cls.Status.PENDING,
        }
        target_status = status_map.get(service_request.status, cls.Status.COMPLETED)
        
        provider_user = None
        if hasattr(service_request, 'service') and service_request.service and hasattr(service_request.service, 'provider') and service_request.service.provider:
            provider_user = getattr(service_request.service.provider, 'user', None)

        base_price = service_request.service.price if service_request.service else Decimal("0.00")
        discount = service_request.discount_amount or Decimal("0.00")
        final_price = service_request.price if service_request.price is not None else max(Decimal("0.00"), base_price - discount)

        if receipt:
            if receipt.status != target_status or receipt.total_amount != final_price:
                receipt.status = target_status
                receipt.total_amount = final_price
                receipt.amount_iqd = final_price * receipt.exchange_rate
                receipt.save(update_fields=['status', 'total_amount', 'amount_iqd', 'updated_at'])
            return receipt

        receipt_num = f"REC-REQ-{service_request.pk:05d}"
        notes = (
            "هذا الوصل وثيقة مالية رسمية صادرة من منصة خدماتي. "
            "الخدمة مشمولة بضمان استرداد الأموال وحماية المشتري المعتمدة حتى استلام العمل بالكامل."
        )
        metadata = {
            'service_id': service_request.service.id if service_request.service else None,
            'service_title': service_request.service.title if service_request.service else '',
            'service_slug': service_request.service.slug if service_request.service else '',
            'category_name': service_request.service.category.name if service_request.service and service_request.service.category else '',
            'provider_name': service_request.service.provider.display_name if service_request.service and service_request.service.provider else '',
            'customer_username': service_request.customer.username,
            'customer_email': service_request.contact_email or service_request.customer.email,
            'customer_phone': service_request.contact_phone,
            'coupon_code': service_request.coupon.code if service_request.coupon else '',
            'request_created_at': service_request.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        receipt = cls(
            receipt_number=receipt_num,
            receipt_type=cls.ReceiptType.ORDER,
            status=target_status,
            user=service_request.customer,
            counterpart_user=provider_user,
            service_request=service_request,
            title=f"طلب خدمة: {service_request.service.title if service_request.service else 'خدمة مخصصة'}",
            subtotal=base_price,
            discount_amount=discount,
            tax_or_fee=Decimal("0.00"),
            total_amount=final_price,
            exchange_rate=Decimal("1500.00"),
            payment_method_name="رصيد محفظة خدماتي الإلكترونية",
            payment_reference=f"ORD-{service_request.pk:05d}",
            metadata=metadata,
            notes=notes,
            issued_at=service_request.created_at or timezone.now()
        )
        receipt.save()
        return receipt

    @classmethod
    def create_or_get_for_deposit(cls, deposit_request, base_url=""):
        receipt = cls.objects.filter(deposit_request=deposit_request).first()
        status_map = {
            deposit_request.Status.APPROVED: cls.Status.COMPLETED,
            deposit_request.Status.PENDING: cls.Status.PENDING,
            deposit_request.Status.REJECTED: cls.Status.CANCELLED,
        }
        target_status = status_map.get(deposit_request.status, cls.Status.PENDING)

        method_name = deposit_request.deposit_method.name if deposit_request.deposit_method else "تحويل يدوي"
        amount = deposit_request.amount

        if receipt:
            if receipt.status != target_status or receipt.total_amount != amount:
                receipt.status = target_status
                receipt.total_amount = amount
                receipt.amount_iqd = amount * receipt.exchange_rate
                receipt.save(update_fields=['status', 'total_amount', 'amount_iqd', 'updated_at'])
            return receipt

        receipt_num = f"REC-{deposit_request.reference_id}"
        notes = (
            "إيصال شحن رصيد رسمي صادر وموثق من منصة خدماتي. "
            "يُعتمد هذا الوصل كإثبات رسمي لإيداع الأموال في حساب المحفظة الإلكترونية للمستخدم."
        )
        metadata = {
            'sender_name': deposit_request.sender_name,
            'sender_phone': deposit_request.sender_phone,
            'transaction_reference': deposit_request.transaction_reference,
            'deposit_method_name': method_name,
            'account_number': deposit_request.deposit_method.account_number if deposit_request.deposit_method else '',
            'admin_notes': deposit_request.admin_notes,
            'has_receipt_image': bool(deposit_request.receipt_image),
        }

        receipt = cls(
            receipt_number=receipt_num,
            receipt_type=cls.ReceiptType.DEPOSIT,
            status=target_status,
            user=deposit_request.wallet.user,
            deposit_request=deposit_request,
            title=f"شحن رصيد المحفظة عبر {method_name}",
            subtotal=amount,
            discount_amount=Decimal("0.00"),
            tax_or_fee=Decimal("0.00"),
            total_amount=amount,
            exchange_rate=Decimal("1500.00"),
            payment_method_name=method_name,
            payment_reference=deposit_request.transaction_reference or deposit_request.reference_id,
            metadata=metadata,
            notes=notes,
            issued_at=deposit_request.created_at or timezone.now()
        )
        receipt.save()
        return receipt

    @classmethod
    def create_or_get_for_withdrawal(cls, withdrawal_request, base_url=""):
        receipt = cls.objects.filter(withdrawal_request=withdrawal_request).first()
        status_map = {
            withdrawal_request.Status.COMPLETED: cls.Status.COMPLETED,
            withdrawal_request.Status.PENDING: cls.Status.PENDING,
            withdrawal_request.Status.PROCESSING: cls.Status.PENDING,
            withdrawal_request.Status.REJECTED: cls.Status.CANCELLED,
        }
        target_status = status_map.get(withdrawal_request.status, cls.Status.PENDING)
        amount = withdrawal_request.amount
        method_name = withdrawal_request.get_method_display()

        if receipt:
            if receipt.status != target_status or receipt.total_amount != amount:
                receipt.status = target_status
                receipt.total_amount = amount
                receipt.amount_iqd = amount * receipt.exchange_rate
                receipt.save(update_fields=['status', 'total_amount', 'amount_iqd', 'updated_at'])
            return receipt

        ref_code = f"WTH-{withdrawal_request.pk:05d}"
        receipt_num = f"REC-{ref_code}"
        notes = (
            "سند سحب مالي رسمي صادر من منصة خدماتي. "
            "يوثق تحويل المستحقات والأرباح المالية للعميل عبر وسيلة الدفع المحددة."
        )
        metadata = {
            'withdrawal_method': method_name,
            'account_info': withdrawal_request.account_info,
            'admin_notes': withdrawal_request.admin_notes,
            'processed_at': withdrawal_request.processed_at.strftime('%Y-%m-%d %H:%M:%S') if withdrawal_request.processed_at else None,
        }

        receipt = cls(
            receipt_number=receipt_num,
            receipt_type=cls.ReceiptType.WITHDRAWAL,
            status=target_status,
            user=withdrawal_request.wallet.user,
            withdrawal_request=withdrawal_request,
            title=f"سحب رصيد وأرباح عبر {method_name}",
            subtotal=amount,
            discount_amount=Decimal("0.00"),
            tax_or_fee=Decimal("0.00"),
            total_amount=amount,
            exchange_rate=Decimal("1500.00"),
            payment_method_name=method_name,
            payment_reference=ref_code,
            metadata=metadata,
            notes=notes,
            issued_at=withdrawal_request.created_at or timezone.now()
        )
        receipt.save()
        return receipt

    @classmethod
    def create_or_get_for_transaction(cls, transaction_obj, base_url=""):
        if transaction_obj.related_order:
            return cls.create_or_get_for_request(transaction_obj.related_order, base_url=base_url)

        if transaction_obj.reference_id and transaction_obj.reference_id.startswith("DEP-"):
            dep = DepositRequest.objects.filter(reference_id=transaction_obj.reference_id).first()
            if dep:
                return cls.create_or_get_for_deposit(dep, base_url=base_url)

        if transaction_obj.reference_id and transaction_obj.reference_id.startswith("WTH-"):
            try:
                wth_pk = int(transaction_obj.reference_id.replace("WTH-", ""))
                wth = WithdrawalRequest.objects.filter(pk=wth_pk).first()
                if wth:
                    return cls.create_or_get_for_withdrawal(wth, base_url=base_url)
            except Exception:
                pass

        receipt = cls.objects.filter(transaction=transaction_obj).first()
        if receipt:
            return receipt

        type_map = {
            transaction_obj.TransactionType.DEPOSIT: cls.ReceiptType.DEPOSIT,
            transaction_obj.TransactionType.WITHDRAWAL: cls.ReceiptType.WITHDRAWAL,
            transaction_obj.TransactionType.ORDER_PAYMENT: cls.ReceiptType.ORDER,
            transaction_obj.TransactionType.REFUND: cls.ReceiptType.REFUND,
            transaction_obj.TransactionType.TRANSFER: cls.ReceiptType.TRANSFER,
        }
        receipt_type = type_map.get(transaction_obj.transaction_type, cls.ReceiptType.GENERAL)

        status_map = {
            transaction_obj.TransactionStatus.COMPLETED: cls.Status.COMPLETED,
            transaction_obj.TransactionStatus.PENDING: cls.Status.PENDING,
            transaction_obj.TransactionStatus.FAILED: cls.Status.CANCELLED,
            transaction_obj.TransactionStatus.CANCELED: cls.Status.CANCELLED,
        }
        target_status = status_map.get(transaction_obj.status, cls.Status.COMPLETED)

        receipt_num = f"REC-TXN-{transaction_obj.pk:06d}"
        receipt = cls(
            receipt_number=receipt_num,
            receipt_type=receipt_type,
            status=target_status,
            user=transaction_obj.wallet.user,
            transaction=transaction_obj,
            title=transaction_obj.description or f"معاملة مالية: {transaction_obj.get_transaction_type_display()}",
            subtotal=transaction_obj.amount,
            discount_amount=Decimal("0.00"),
            tax_or_fee=transaction_obj.fee,
            total_amount=transaction_obj.amount,
            exchange_rate=Decimal("1500.00"),
            payment_method_name="محفظة خدماتي الإلكترونية",
            payment_reference=transaction_obj.reference_id or f"TXN-{transaction_obj.pk}",
            notes="وصل معاملة مالية موثقة من نظام محفظة خدماتي.",
            issued_at=transaction_obj.created_at or timezone.now()
        )
        receipt.save()
        return receipt
