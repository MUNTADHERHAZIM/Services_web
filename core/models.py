from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class AuditLog(models.Model):
    """
    سجل نشاطات النظام - System Audit Log
    """
    class ActionType(models.TextChoices):
        LOGIN = 'login', _('تسجيل دخول')
        LOGOUT = 'logout', _('تسجيل خروج')
        FAILED_LOGIN = 'failed_login', _('فشل تسجيل دخول')
        CREATE_RECORD = 'create', _('إنشاء سجل')
        UPDATE_RECORD = 'update', _('تعديل سجل')
        DELETE_RECORD = 'delete', _('حذف سجل')
        VERIFICATION = 'verification', _('توثيق حساب')
        SECURITY = 'security', _('أمن وحماية')
        WALLET = 'wallet', _('عمليات مالية')

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('المستخدم')
    )
    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        verbose_name=_('نوع النشاط')
    )
    description = models.TextField(
        verbose_name=_('التفاصيل')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('عنوان IP')
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('متصفح المستخدم')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ النشاط')
    )

    class Meta:
        verbose_name = _('سجل النشاط')
        verbose_name_plural = _('سجل النشاطات')
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.username if self.user else "زائر"
        return f"{user_str} - {self.get_action_type_display()} - {self.created_at}"


class PromotionalBanner(models.Model):
    """
    نموذج البنرات والإعلانات الترويجية المتقدمة
    """
    class BannerType(models.TextChoices):
        ANNOUNCEMENT = 'announcement', _('شريط إعلاني علوي (Top Bar)')
        HERO_SLIDER = 'hero_slider', _('بنر ترويجي رئيسي (Hero Slider)')
        PROMO_CARD = 'promo_card', _('بطاقة عرض ترويجي (Flash Deal / Card)')
        POPUP = 'popup', _('إعلان منبثق (Modal Popup)')

    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان الإعلان أو العرض')
    )
    subtitle = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_('العنوان الفرعي أو التوضيح')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('تفاصيل العرض')
    )
    banner_type = models.CharField(
        max_length=30,
        choices=BannerType.choices,
        default=BannerType.ANNOUNCEMENT,
        verbose_name=_('نوع وموضع الإعلان')
    )
    
    # CTA & Links
    cta_text = models.CharField(
        max_length=60,
        default='استفد من العرض الآن',
        verbose_name=_('نص زر التفاعل')
    )
    cta_url = models.CharField(
        max_length=300,
        default='/services/',
        verbose_name=_('رابط الزر أو الخدمة')
    )
    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('كوبون الخصم المرفق'),
        help_text=_('إذا وُجد، سيتاح للمستخدم نسخه بضغطة زر مباشرة')
    )
    
    # Visual Styling
    badge_text = models.CharField(
        max_length=50,
        blank=True,
        default='عرض خاص 🔥',
        verbose_name=_('نص الشارة')
    )
    image = models.ImageField(
        upload_to='banners/',
        blank=True,
        null=True,
        verbose_name=_('صورة الإعلان')
    )
    bg_gradient = models.CharField(
        max_length=150,
        blank=True,
        default='linear-gradient(135deg, #059669 0%, #0f172a 100%)',
        verbose_name=_('تدرج الخلفية (CSS Gradient)')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='bi-lightning-charge-fill',
        verbose_name=_('أيقونة Bootstrap')
    )

    # Display conditions & scheduling
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب والأولوية')
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ البدء')
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الانتهاء')
    )
    clicks_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد النقرات والتفاعل')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('إعلان / بنر ترويجي')
        verbose_name_plural = _('الإعلانات والبنرات الترويجية')
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"[{self.get_banner_type_display()}] {self.title}"

    def increment_clicks(self):
        """زيادة عدد النقرات"""
        self.clicks_count += 1
        self.save(update_fields=['clicks_count'])


class Coupon(models.Model):
    """
    نموذج قسائم وكوبونات الخصم للمنصة
    """
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('نسبة مئوية (%)')
        FIXED = 'fixed', _('مبلغ ثابت ($)')

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('كود الكوبون'),
        help_text=_('مثال: SAVE20, RAMADAN, WELCOME')
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('الوصف الترويجي')
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
        verbose_name=_('نوع الخصم')
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('قيمة الخصم (% أو $)')
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('الحد الأدنى لقيمة الطلب')
    )
    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('الحد الأقصى للخصم (للنسب المئوية)')
    )
    max_uses = models.PositiveIntegerField(
        default=100,
        verbose_name=_('الحد الأقصى للاستخدام الإجمالي')
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('مرات الاستخدام الفعلية')
    )
    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('صالح من تاريخ')
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('صالح حتى تاريخ')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('مفعل')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))

    class Meta:
        verbose_name = _('كوبون خصم')
        verbose_name_plural = _('كوبونات الخصم')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == self.DiscountType.PERCENTAGE else '$'})"

    def is_valid_for(self, order_amount=0):
        """التحقق من صلاحية الكوبون لمبلغ معين"""
        from django.utils import timezone
        now = timezone.now()

        if not self.is_active:
            return False, _('هذا الكوبون غير مفعّل حالياً.')
        if self.valid_from and now < self.valid_from:
            return False, _('هذا الكوبون لم يبدأ بعد.')
        if self.valid_until and now > self.valid_until:
            return False, _('عذراً، انتهت صلاحية هذا الكوبون.')
        if self.used_count >= self.max_uses:
            return False, _('تم استنفاد الحد الأقصى لاستخدام هذا الكوبون.')
        if order_amount and order_amount < self.min_order_amount:
            return False, _(f'الحد الأدنى لتطبيق هذا الكوبون هو ${self.min_order_amount}.')

        return True, _('كوبون صالح.')

    def calculate_discount(self, order_amount):
        """حساب قيمة الخصم الفعلي لمبلغ الطلب"""
        from decimal import Decimal
        order_amount = Decimal(str(order_amount))
        
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = (self.discount_value / Decimal('100')) * order_amount
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return round(discount, 2)
        else:
            return min(self.discount_value, order_amount)


