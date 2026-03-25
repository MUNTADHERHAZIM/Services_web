"""
Enhanced Admin for Services with Professional Review Management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, Tag, Service, ServiceImage, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """إدارة التقييمات المحسّنة"""
    list_display = [
        'service', 'customer', 'rating_display', 'title', 
        'is_verified_purchase', 'helpful_count', 'is_approved', 
        'has_response', 'created_at'
    ]
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['title', 'comment', 'customer__username', 'service__title']
    readonly_fields = ['helpful_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات التقييم', {
            'fields': ('service', 'customer', 'rating', 'title')
        }),
        ('التفاصيل', {
            'fields': ('comment', 'pros', 'cons')
        }),
        ('التحقق', {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        ('رد مقدم الخدمة', {
            'fields': ('provider_response', 'provider_response_date'),
            'classes': ('collapse',)
        }),
        ('الإحصائيات', {
            'fields': ('helpful_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        """عرض التقييم بالنجوم"""
        stars_html = ''.join(['<i class="bi bi-star-fill text-warning"></i>' for _ in range(obj.rating)])
        stars_html += ''.join(['<i class="bi bi-star text-muted"></i>' for _ in range(5 - obj.rating)])
        return format_html(stars_html)
    rating_display.short_description = 'التقييم'
    
    def has_response(self, obj):
        """هل رد مقدم الخدمة؟"""
        if obj.provider_response:
            return format_html('<i class="bi bi-check-circle-fill text-success"></i> نعم')
        return format_html('<i class="bi bi-x-circle text-muted"></i> لا')
    has_response.short_description = 'رد مقدم الخدمة'
    
    actions = ['approve_reviews', 'unapprove_reviews', 'mark_as_verified']
    
    @admin.action(description='✓ الموافقة على التقييمات المحددة')
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'تمت الموافقة على {updated} تقييم.')
    
    @admin.action(description='✗ إلغاء الموافقة')
    def unapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'تم إلغاء الموافقة على {updated} تقييم.')
    
    @admin.action(description='✓ تحديد كشراء موثق')
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified_purchase=True)
        self.message_user(request, f'تم تحديد {updated} تقييم كشراء موثق.')
