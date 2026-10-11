"""
Analytics Models - نماذج التحليلات
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ServiceView(models.Model):
    """
    تسجيل مشاهدة خدمة
    """

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="analytics_views",
        verbose_name=_("الخدمة"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_views",
        verbose_name=_("المستخدم"),
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name=_("عنوان IP")
    )
    user_agent = models.CharField(
        max_length=500, blank=True, verbose_name=_("متصفح المستخدم")
    )
    referrer = models.URLField(blank=True, verbose_name=_("المصدر"))
    device_type = models.CharField(
        max_length=20,
        choices=[
            ("desktop", _("كمبيوتر")),
            ("mobile", _("هاتف")),
            ("tablet", _("جهاز لوحي")),
        ],
        default="desktop",
        verbose_name=_("نوع الجهاز"),
    )
    country = models.CharField(max_length=100, blank=True, verbose_name=_("الدولة"))
    city = models.CharField(max_length=100, blank=True, verbose_name=_("المدينة"))
    viewed_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ المشاهدة")
    )

    class Meta:
        verbose_name = _("مشاهدة خدمة")
        verbose_name_plural = _("مشاهدات الخدمات")
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.service.title} - {self.viewed_at}"


class SearchAnalytics(models.Model):
    """
    تحليلات البحث
    """

    query = models.CharField(max_length=200, verbose_name=_("كلمة البحث"))
    search_count = models.PositiveIntegerField(
        default=0, verbose_name=_("عدد مرات البحث")
    )
    results_count_avg = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("متوسط عدد النتائج")
    )
    clicks_count = models.PositiveIntegerField(default=0, verbose_name=_("عدد النقرات"))
    conversion_count = models.PositiveIntegerField(
        default=0, verbose_name=_("عدد التحويلات")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("تحليل بحث")
        verbose_name_plural = _("تحليلات البحث")
        ordering = ["-search_count"]

    def __str__(self):
        return f"{self.query} ({self.search_count})"


class ProviderStats(models.Model):
    """
    إحصائيات المزود
    """

    provider = models.OneToOneField(
        "accounts.Provider",
        on_delete=models.CASCADE,
        related_name="stats",
        verbose_name=_("مزود الخدمة"),
    )
    total_earnings = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name=_("إجمالي الأرباح")
    )
    available_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name=_("الرصيد المتاح")
    )
    pending_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name=_("الرصيد المعلق")
    )
    total_orders = models.PositiveIntegerField(
        default=0, verbose_name=_("إجمالي الطلبات")
    )
    completed_orders = models.PositiveIntegerField(
        default=0, verbose_name=_("الطلبات المكتملة")
    )
    canceled_orders = models.PositiveIntegerField(
        default=0, verbose_name=_("الطلبات الملغاة")
    )
    response_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=100, verbose_name=_("معدل الاستجابة %")
    )
    delivery_on_time_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        verbose_name=_("معدل التسليم في الوقت %"),
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ التحديث"))

    class Meta:
        verbose_name = _("إحصائيات مزود")
        verbose_name_plural = _("إحصائيات المزودين")

    def __str__(self):
        return f"{self.provider.user.username} Stats"

    @property
    def completion_rate(self):
        if self.total_orders == 0:
            return 0
        return round((self.completed_orders / self.total_orders) * 100, 1)
