from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from .models import AuditLog, PromotionalBanner, Coupon

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag_display')
    list_filter = ('action_flag', 'content_type', 'action_time')
    search_fields = ('object_repr', 'change_message', 'user__username')
    date_hierarchy = 'action_time'

    def action_flag_display(self, obj):
        if obj.is_addition():
            return format_html('<span style="color: #10b981; font-weight: bold;"><i class="bi bi-plus-circle-fill"></i> إضافة</span>')
        elif obj.is_change():
            return format_html('<span style="color: #f59e0b; font-weight: bold;"><i class="bi bi-pencil-square"></i> تعديل</span>')
        elif obj.is_deletion():
            return format_html('<span style="color: #ef4444; font-weight: bold;"><i class="bi bi-trash-fill"></i> حذف</span>')
        return str(obj.action_flag)
    action_flag_display.short_description = 'نوع العملية'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_badge', 'description', 'ip_address', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('user', 'action_type', 'description', 'ip_address', 'user_agent', 'created_at')
    date_hierarchy = 'created_at'

    def action_badge(self, obj):
        colors = {
            'login': '#10b981',
            'logout': '#64748b',
            'failed_login': '#ef4444',
            'create': '#3b82f6',
            'update': '#f59e0b',
            'delete': '#dc2626',
            'verification': '#8b5cf6',
            'security': '#ec4899',
            'wallet': '#14b8a6',
        }
        color = colors.get(obj.action_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 0.75rem;">{}</span>',
            color,
            obj.get_action_type_display()
        )
    action_badge.short_description = 'نوع النشاط'


@admin.register(PromotionalBanner)
class PromotionalBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'badge_text', 'coupon_code', 'is_active', 'order', 'clicks_count', 'created_at')
    list_filter = ('banner_type', 'is_active', 'created_at')
    search_fields = ('title', 'subtitle', 'description', 'coupon_code')
    list_editable = ('is_active', 'order')
    fieldsets = (
        ('معلومات الإعلان والعرض', {
            'fields': ('title', 'subtitle', 'description', 'banner_type', 'badge_text', 'icon')
        }),
        ('التفاعل والروابط والكوبون', {
            'fields': ('cta_text', 'cta_url', 'coupon_code')
        }),
        ('المظهر والتصميم', {
            'fields': ('image', 'bg_gradient')
        }),
        ('حالة التفعيل والجدولة', {
            'fields': ('is_active', 'order', 'start_date', 'end_date', 'clicks_count')
        }),
    )
    readonly_fields = ('clicks_count',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount', 'used_count', 'max_uses', 'is_active', 'valid_until')
    list_filter = ('discount_type', 'is_active', 'valid_until')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
    fieldsets = (
        ('معلومات الكوبون', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('قيمة الخصم والشروط', {
            'fields': ('discount_type', 'discount_value', 'min_order_amount', 'max_discount_amount')
        }),
        ('حدود الاستخدام والصلاحية', {
            'fields': ('max_uses', 'used_count', 'valid_from', 'valid_until')
        }),
    )


