"""
Enhanced Admin for Provider Agreements and Violations
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import ProviderAgreement, ProviderViolation


@admin.register(ProviderAgreement)
class ProviderAgreementAdmin(admin.ModelAdmin):
    """إدارة تعهدات مقدمي الخدمات"""
    list_display = [
        'provider', 'full_name', 'national_id', 'specialty',
        'is_fully_signed_display', 'commission_display', 
        'is_verified_display', 'signed_date'
    ]
    list_filter = ['is_active', 'verified_at', 'signed_date', 'specialty']
    search_fields = ['full_name', 'national_id', 'phone_number', 'provider__display_name']
    readonly_fields = ['created_at', 'updated_at', 'id_card_preview', 'signature_preview']
    date_hierarchy = 'signed_date'
    actions = ['verify_agreements', 'deactivate_agreements']
    
    fieldsets = (
        ('معلومات المتعهد', {
            'fields': ('provider', 'full_name', 'national_id', 'address', 'phone_number', 'specialty')
        }),
        ('الالتزامات', {
            'fields': ('conduct_agreement', 'professional_standards', 'commission_agreement', 'privacy_agreement'),
            'classes': ('wide',)
        }),
        ('العمولات', {
            'fields': ('commission_percentage', 'commission_fixed')
        }),
        ('الوثائق', {
            'fields': ('id_card_front', 'id_card_back', 'id_card_preview', 'signature_image', 'signature_preview', 'thumbprint_image'),
            'classes': ('collapse',)
        }),
        ('التحقق والتوقيع', {
            'fields': ('signed_date', 'verified_by', 'verified_at', 'is_active')
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_fully_signed_display(self, obj):
        """عرض حالة التوقيع"""
        if obj.is_fully_signed():
            return format_html('<span class="badge bg-success">✓ موقع بالكامل</span>')
        return format_html('<span class="badge bg-warning">⚠ غير مكتمل</span>')
    is_fully_signed_display.short_description = 'حالة التوقيع'
    
    def commission_display(self, obj):
        """عرض العمولة"""
        if obj.commission_fixed > 0:
            return format_html('<strong>{} دينار</strong>', obj.commission_fixed)
        return format_html('<strong>{}%</strong>', obj.commission_percentage)
    commission_display.short_description = 'العمولة'
    
    def is_verified_display(self, obj):
        """عرض حالة التحقق"""
        if obj.verified_at:
            return format_html(
                '<span class="badge bg-success"><i class="bi bi-patch-check-fill"></i> موثق</span><br>'
                '<small class="text-muted">{}</small>',
                obj.verified_at.strftime('%d/%m/%Y')
            )
        return format_html('<span class="badge bg-secondary">غير موثق</span>')
    is_verified_display.short_description = 'حالة التحقق'
    
    def id_card_preview(self, obj):
        """معاينة البطاقة"""
        if obj.id_card_front:
            html = f'<div class="row">'
            html += f'<div class="col-md-6">'
            html += f'<p><strong>الوجه الأمامي:</strong></p>'
            html += f'<a href="{obj.id_card_front.url}" target="_blank">'
            html += f'<img src="{obj.id_card_front.url}" style="max-width: 300px; border: 1px solid #ddd; padding: 5px;" />'
            html += f'</a></div>'
            if obj.id_card_back:
                html += f'<div class="col-md-6">'
                html += f'<p><strong>الوجه الخلفي:</strong></p>'
                html += f'<a href="{obj.id_card_back.url}" target="_blank">'
                html += f'<img src="{obj.id_card_back.url}" style="max-width: 300px; border: 1px solid #ddd; padding: 5px;" />'
                html += f'</a></div>'
            html += f'</div>'
            return format_html(html)
        return format_html('<span class="text-muted">لم يتم رفع صورة البطاقة</span>')
    id_card_preview.short_description = 'معاينة البطاقة الموحدة'
    
    def signature_preview(self, obj):
        """معاينة التوقيع"""
        if obj.signature_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 200px; border: 2px solid #333; padding: 10px; background: white;" />'
                '</a>',
                obj.signature_image.url, obj.signature_image.url
            )
        return format_html('<span class="text-muted">لم يتم رفع التوقيع</span>')
    signature_preview.short_description = 'معاينة التوقيع'
    
    @admin.action(description='✓ التحقق من التعهدات المحددة')
    def verify_agreements(self, request, queryset):
        updated = 0
        for agreement in queryset.filter(verified_at__isnull=True):
            if agreement.is_fully_signed():
                agreement.verified_by = request.user
                agreement.verified_at = timezone.now()
                agreement.is_active = True
                agreement.save()
                updated += 1
        self.message_user(request, f'تم التحقق من {updated} تعهد.')
    
    @admin.action(description='✗ تعطيل التعهدات')
    def deactivate_agreements(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم تعطيل {updated} تعهد.')


@admin.register(ProviderViolation)
class ProviderViolationAdmin(admin.ModelAdmin):
    """إدارة مخالفات مقدمي الخدمات"""
    list_display = [
        'provider', 'violation_type_display', 'severity_display',
        'is_resolved', 'reported_by', 'created_at'
    ]
    list_filter = ['violation_type', 'severity', 'is_resolved', 'created_at']
    search_fields = ['provider__display_name', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات المخالفة', {
            'fields': ('provider', 'violation_type', 'severity', 'description')
        }),
        ('الأدلة', {
            'fields': ('evidence',),
            'classes': ('collapse',)
        }),
        ('الإجراءات', {
            'fields': ('action_taken', 'is_resolved')
        }),
        ('معلومات التقرير', {
            'fields': ('reported_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def violation_type_display(self, obj):
        """عرض نوع المخالفة بألوان"""
        colors = {
            'conduct': 'danger',
            'quality': 'warning',
            'pricing': 'info',
            'commission': 'danger',
            'privacy': 'dark',
            'other': 'secondary'
        }
        color = colors.get(obj.violation_type, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_violation_type_display()
        )
    violation_type_display.short_description = 'نوع المخالفة'
    
    def severity_display(self, obj):
        """عرض درجة الخطورة"""
        colors = {1: 'success', 2: 'warning', 3: 'danger'}
        labels = {1: 'بسيطة', 2: 'متوسطة', 3: 'خطيرة'}
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors[obj.severity], labels[obj.severity]
        )
    severity_display.short_description = 'درجة الخطورة'
    
    actions = ['mark_as_resolved']
    
    @admin.action(description='✓ تحديد كمحلولة')
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f'تم تحديد {updated} مخالفة كمحلولة.')
