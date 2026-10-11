"""
Favorites Models - نماذج المفضلة
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class FavoriteService(models.Model):
    """
    الخدمات المفضلة
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_services",
        verbose_name=_("المستخدم"),
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("الخدمة"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("تاريخ الإضافة")
    )

    class Meta:
        verbose_name = _("خدمة مفضلة")
        verbose_name_plural = _("الخدمات المفضلة")
        unique_together = ["user", "service"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.service.title}"


class RecentlyViewed(models.Model):
    """
    الخدمات التي شاهدها المستخدم مؤخراً
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recently_viewed",
        verbose_name=_("المستخدم"),
    )
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="viewed_by",
        verbose_name=_("الخدمة"),
    )
    viewed_at = models.DateTimeField(auto_now=True, verbose_name=_("تاريخ المشاهدة"))

    class Meta:
        verbose_name = _("خدمة مشاهدت")
        verbose_name_plural = _("الخدمات المشاهدت")
        unique_together = ["user", "service"]
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.user.username} viewed {self.service.title}"


class SearchHistory(models.Model):
    """
    سجل البحث للمستخدم
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="search_history",
        verbose_name=_("المستخدم"),
    )
    query = models.CharField(max_length=200, verbose_name=_("كلمة البحث"))
    results_count = models.PositiveIntegerField(
        default=0, verbose_name=_("عدد النتائج")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ البحث"))

    class Meta:
        verbose_name = _("سجل بحث")
        verbose_name_plural = _("سجلات البحث")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.query}"
