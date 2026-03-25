"""
Reviews Models - نماذج التقييمات والمراجعات
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from services.models import Service
from requests.models import ServiceRequest


class Review(models.Model):
    """تقييم ومراجعة للخدمة"""
    
    # Relations
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='الخدمة'
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        verbose_name='العميل'
    )
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
        blank=True,
        verbose_name='الطلب المرتبط'
    )
    
    # Rating and Content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='التقييم',
        help_text='من 1 إلى 5 نجوم'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان المراجعة',
        blank=True
    )
    comment = models.TextField(
        verbose_name='التعليق',
        blank=True
    )
    
    # Metadata
    is_approved = models.BooleanField(
        default=True,
        verbose_name='موافق عليها',
        help_text='للمراجعة من الإدارة'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'مراجعة'
        verbose_name_plural = 'المراجعات'
        ordering = ['-created_at']
        unique_together = ['service', 'customer']  # مراجعة واحدة لكل عميل
    
    def __str__(self):
        return f'{self.customer.get_full_name()} - {self.service.title} ({self.rating}★)'
    
    @property
    def rating_stars(self):
        """عرض النجوم"""
        return '★' * self.rating + '☆' * (5 - self.rating)


class ReviewImage(models.Model):
    """صور المراجعة"""
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='المراجعة'
    )
    image = models.ImageField(
        upload_to='reviews/%Y/%m/',
        verbose_name='الصورة'
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='التعليق'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')
    
    class Meta:
        verbose_name = 'صورة مراجعة'
        verbose_name_plural = 'صور المراجعات'
    
    def __str__(self):
        return f'صورة - {self.review}'


class ReviewResponse(models.Model):
    """رد مقدم الخدمة على المراجعة"""
    
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='response',
        verbose_name='المراجعة'
    )
    provider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_responses',
        verbose_name='المزود'
    )
    response_text = models.TextField(verbose_name='الرد')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'رد على مراجعة'
        verbose_name_plural = 'الردود على المراجعات'
    
    def __str__(self):
        return f'رد {self.provider.get_full_name()} على {self.review}'
