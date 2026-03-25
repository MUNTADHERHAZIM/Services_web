"""
Accounts Admin - لوحة إدارة الحسابات
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils import timezone
from .models import Provider, UserProfile, ProviderAgreement, ProviderViolation, ProviderAgreement, ProviderViolation


class ProviderInline(admin.StackedInline):
    """عرض مقدم الخدمة داخل صفحة المستخدم"""
    model = Provider
    can_delete = False
    verbose_name = 'ملف مقدم الخدمة'
    verbose_name_plural = 'ملف مقدم الخدمة'
    fk_name = 'user'


class UserProfileInline(admin.StackedInline):
    """عرض الملف الشخصي داخل صفحة المستخدم"""
    model = UserProfile
    can_delete = False
    verbose_name = 'الملف الشخصي الموسع'
    verbose_name_plural = 'الملف الشخصي الموسع'
    fk_name = 'user'
    readonly_fields = ['completion_percentage', 'profile_completed', 'verified_at', 'verified_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('المعلومات الشخصية', {
            'fields': ('profile_picture', 'date_of_birth', 'gender')
        }),
        ('معلومات التواصل', {
            'fields': ('phone_number', 'alternate_phone')
        }),
        ('العنوان', {
            'fields': ('address', 'city', 'district', 'postal_code')
        }),
        ('التحقق من الهوية', {
            'fields': ('id_type', 'id_number', 'id_document', 'id_verified', 'verified_at', 'verified_by', 'verification_notes'),
            'classes': ('wide',)
        }),
        ('اكتمال الملف', {
            'fields': ('completion_percentage', 'profile_completed'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class UserAdmin(BaseUserAdmin):
    """تخصيص إدارة المستخدمين"""
    inlines = [UserProfileInline, ProviderInline]
    list_display = ['username', 'email', 'full_name', 'is_verified_display', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups', 'profile__id_verified']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'profile__phone_number']
    ordering = ['-date_joined']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name else obj.username
    full_name.short_description = 'الاسم الكامل'
    
    def is_verified_display(self, obj):
        if hasattr(obj, 'profile') and obj.profile.id_verified:
            return format_html('<span class="badge bg-success">✓ موثق</span>')
        elif hasattr(obj, 'profile') and obj.profile.id_document:
            return format_html('<span class="badge bg-warning">⏳ قيد المراجعة</span>')
        return format_html('<span class="badge bg-secondary">غير موثق</span>')
    is_verified_display.short_description = 'حالة التوثيق'


# إعادة تسجيل User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    """إدارة مقدمي الخدمات"""
    list_display = [
        'display_name', 'user', 'phone', 'is_verified_badge', 
        'is_active_badge', 'services_count', 'created_at'
    ]
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['display_name', 'user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'services_count']
    list_editable = ['is_verified', 'is_active'] if False else []  # للتعديل المباشر
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('user', 'display_name', 'bio')
        }),
        ('معلومات التواصل', {
            'fields': ('phone', 'avatar')
        }),
        ('الحالة', {
            'fields': ('is_verified', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span class="badge bg-success">✓ موثق</span>')
        return format_html('<span class="badge bg-secondary">غير موثق</span>')
    is_verified_badge.short_description = 'التوثيق'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge bg-success">نشط</span>')
        return format_html('<span class="badge bg-danger">غير نشط</span>')
    is_active_badge.short_description = 'الحالة'

    def services_count(self, obj):
        count = obj.get_services_count()
        return format_html('<span class="badge bg-info">{}</span>', count)
    services_count.short_description = 'عدد الخدمات'

    actions = ['verify_providers', 'unverify_providers', 'activate_providers', 'deactivate_providers']

    @admin.action(description='توثيق مقدمي الخدمات المحددين')
    def verify_providers(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'تم توثيق {updated} مقدم خدمة.')

    @admin.action(description='إلغاء توثيق مقدمي الخدمات المحددين')
    def unverify_providers(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'تم إلغاء توثيق {updated} مقدم خدمة.')

    @admin.action(description='تفعيل مقدمي الخدمات المحددين')
    def activate_providers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'تم تفعيل {updated} مقدم خدمة.')

    @admin.action(description='تعطيل مقدمي الخدمات المحددين')
    def deactivate_providers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم تعطيل {updated} مقدم خدمة.')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """إدارة الملفات الشخصية للمستخدمين"""
    list_display = [
        'user', 'get_full_name', 'phone_number', 'city', 
        'id_type', 'verification_status_badge', 'completion_badge', 'created_at'
    ]
    list_filter = ['id_verified', 'id_type', 'gender', 'profile_completed', 'created_at']
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'phone_number', 'city', 'id_number'
    ]
    readonly_fields = [
        'completion_percentage', 'profile_completed', 'verified_at', 
        'verified_by', 'created_at', 'updated_at', 'document_preview'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user',)
        }),
        ('المعلومات الشخصية', {
            'fields': ('profile_picture', 'date_of_birth', 'gender')
        }),
        ('معلومات التواصل', {
            'fields': ('phone_number', 'alternate_phone')
        }),
        ('العنوان', {
            'fields': ('address', 'city', 'district', 'postal_code')
        }),
        ('وثيقة الهوية', {
            'fields': (
                'id_type', 'id_number', 'id_document', 'document_preview',
                'id_verified', 'verified_at', 'verified_by', 'verification_notes'
            ),
            'classes': ('wide',)
        }),
        ('حالة الملف الشخصي', {
            'fields': ('completion_percentage', 'profile_completed')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ( 'collapse',)
        }),
    )
    
    # Custom methods
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    get_full_name.short_description = 'الاسم الكامل'
    
    def verification_status_badge(self, obj):
        status = obj.get_verification_status()
        colors = {
            'verified': 'success',
            'pending': 'warning',
            'unverified': 'secondary'
        }
        color = colors.get(status['status'], 'secondary')
        return format_html(
            '<span class="badge bg-{}" style="font-size: 11px;"><i class="bi {}"></i> {}</span>',
            color, status['icon'], status['label']
        )
    verification_status_badge.short_description = 'حالة التوثيق'
    
    def completion_badge(self, obj):
        percentage = obj.completion_percentage
        if percentage >= 80:
            color = 'success'
        elif percentage >= 50:
            color = 'warning'
        else:
            color = 'danger'
        return format_html(
            '<div class="progress" style="width: 100px;">' 
            '<div class="progress-bar bg-{}" style="width: {}%">{}%</div>'
            '</div>',
            color, percentage, percentage
        )
    completion_badge.short_description = 'نسبة الاكتمال'
    
    def document_preview(self, obj):
        """معاينة صورة الوثيقة"""
        if obj.id_document:
            if obj.id_document.name.endswith('.pdf'):
                return format_html(
                    '<a href="{}" target="_blank" class="btn btn-sm btn-primary">' 
                    '<i class="bi bi-file-pdf"></i> عرض PDF</a>',
                    obj.id_document.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank">' 
                    '<img src="{}" style="max-width: 300px; max-height: 200px; border: 1px solid #ddd; padding: 5px;"/>' 
                    '</a>',
                    obj.id_document.url, obj.id_document.url
                )
        return format_html('<span class="text-muted">لم يتم رفع وثيقة</span>')
    document_preview.short_description = 'معاينة الوثيقة'
    
    # Custom actions
    actions = [
        'verify_documents', 'unverify_documents', 
        'mark_profiles_completed', 'send_verification_reminder'
    ]
    
    @admin.action(description='✓ الموافقة على الوثائق المحددة')
    def verify_documents(self, request, queryset):
        updated = 0
        for profile in queryset.filter(id_verified=False, id_document__isnull=False):
            profile.id_verified = True
            profile.verified_at = timezone.now()
            profile.verified_by = request.user
            profile.save()
            updated += 1
            
            # يمكن إضافة إشعار للمستخدم هنا
            # create_notification(profile.user, 'تم التحقق من هويتك بنجاح')
        
        self.message_user(request, f'تم التحقق من {updated} وثيقة بنجاح.')
    
    @admin.action(description='✗ إلغاء التحقق من الوثائق المحددة')
    def unverify_documents(self, request, queryset):
        updated = queryset.update(id_verified=False, verified_at=None, verified_by=None)
        self.message_user(request, f'تم إلغاء التحقق من {updated} وثيقة.')
    
    @admin.action(description='✓ تحديد كمكتمل')
    def mark_profiles_completed(self, request, queryset):
        updated = queryset.update(profile_completed=True)
        self.message_user(request, f'تم تحديد {updated} ملف شخصي كمكتمل.')
    
    @admin.action(description='📧 إرسال تذكير بإكمال الملف')
    def send_verification_reminder(self, request, queryset):
        count = 0
        for profile in queryset.filter(id_verified=False):
            # هنا يمكن إرسال بريد إلكتروني أو إشعار
            # send_email_reminder(profile.user)
            count += 1
        self.message_user(request, f'تم إرسال تذكير لـ {count} مستخدم.')


# ============================================================================
# Provider Agreement & Violations Admin
# ============================================================================

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
        if obj.is_fully_signed():
            return format_html('<span class="badge bg-success">✓ موقع بالكامل</span>')
        return format_html('<span class="badge bg-warning">⚠ غير مكتمل</span>')
    is_fully_signed_display.short_description = 'حالة التوقيع'
    
    def commission_display(self, obj):
        if obj.commission_fixed > 0:
            return format_html('<strong>{} دينار</strong>', obj.commission_fixed)
        return format_html('<strong>{}%</strong>', obj.commission_percentage)
    commission_display.short_description = 'العمولة'
    
    def is_verified_display(self, obj):
        if obj.verified_at:
            return format_html(
                '<span class="badge bg-success"><i class="bi bi-patch-check-fill"></i> موثق</span><br>'
                '<small class="text-muted">{}</small>',
                obj.verified_at.strftime('%d/%m/%Y')
            )
        return format_html('<span class="badge bg-secondary">غير موثق</span>')
    is_verified_display.short_description = 'حالة التحقق'
    
    def id_card_preview(self, obj):
        if obj.id_card_front:
            html = '<div class="row">'
            html += '<div class="col-md-6">'
            html += '<p><strong>الوجه الأمامي:</strong></p>'
            html += f'<a href="{obj.id_card_front.url}" target="_blank">'
            html += f'<img src="{obj.id_card_front.url}" style="max-width: 300px; border: 1px solid #ddd; padding: 5px;" />'
            html += '</a></div>'
            if obj.id_card_back:
                html += '<div class="col-md-6">'
                html += '<p><strong>الوجه الخلفي:</strong></p>'
                html += f'<a href="{obj.id_card_back.url}" target="_blank">'
                html += f'<img src="{obj.id_card_back.url}" style="max-width: 300px; border: 1px solid #ddd; padding: 5px;" />'
                html += '</a></div>'
            html += '</div>'
            return format_html(html)
        return format_html('<span class="text-muted">لم يتم رفع صورة البطاقة</span>')
    id_card_preview.short_description = 'معاينة البطاقة الموحدة'
    
    def signature_preview(self, obj):
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
    actions = ['mark_as_resolved']
    
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
        colors = {1: 'success', 2: 'warning', 3: 'danger'}
        labels = {1: 'بسيطة', 2: 'متوسطة', 3: 'خطيرة'}
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors[obj.severity], labels[obj.severity]
        )
    severity_display.short_description = 'درجة الخطورة'
    
    @admin.action(description='✓ تحديد كمحلولة')
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f'تم تحديد {updated} مخالفة كمحلولة.')
