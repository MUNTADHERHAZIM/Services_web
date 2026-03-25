"""
Services Models - Additional Review Models
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ReviewImage(models.Model):
    """
    صور التقييمات
    """
    review = models.ForeignKey(
        'Review',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('التقييم')
    )
    image = models.ImageField(
        upload_to='reviews/%Y/%m/',
        verbose_name=_('الصورة')
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('الوصف')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الرفع')
    )

    class Meta:
        verbose_name = _('صورة التقييم')
        verbose_name_plural = _('صور التقييمات')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'صورة - {self.review}'


class ReviewHelpful(models.Model):
    """
    تتبع من وجد التقييم مفيداً
    """
    review = models.ForeignKey(
        'Review',
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name=_('التقييم')
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name=_('المستخدم')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ التصويت')
    )

    class Meta:
        verbose_name = _('تصويت مفيد')
        verbose_name_plural = _('تصويتات مفيد')
        unique_together = ['review', 'user']

    def __str__(self):
        return f'{self.user.username} - {self.review}'
