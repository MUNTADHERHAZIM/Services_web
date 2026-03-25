"""
Requests Admin - لوحة إدارة طلبات الخدمات
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ServiceRequest, StatusHistory, Notification


class StatusHistoryInline(admin.TabularInline):
    """سجل تغييرات الحالة داخل صفحة الطلب"""
    model = StatusHistory
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'changed_by', 'notes', 'created_at']
    can_delete = False
    ordering = ['-created_at']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    """إدارة طلبات الخدمات"""
    list_display = [
        'id', 'service_link', 'customer_link', 'status_badge', 
        'contact_info', 'created_at', 'updated_at'
    ]
    list_filter = ['status', 'created_at', 'service__category']
    search_fields = [
        'id', 'service__title', 'customer__username', 
        'customer__email', 'contact_phone', 'contact_email'
    ]
    autocomplete_fields = ['service', 'customer']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [StatusHistoryInline]
    list_per_page = 20
    save_on_top = True

    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('service', 'customer', 'status')
        }),
        ('معلومات التواصل', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('الملاحظات', {
            'fields': ('customer_notes', 'staff_notes')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def service_link(self, obj):
        url = reverse('admin:services_service_change', args=[obj.service.pk])
        return format_html('<a href="{}">{}</a>', url, obj.service.title[:30])
    service_link.short_description = 'الخدمة'

    def customer_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.customer.pk])
        return format_html('<a href="{}">{}</a>', url, obj.customer.username)
    customer_link.short_description = 'العميل'

    def status_badge(self, obj):
        status_colors = {
            'new': ('primary', 'جديد'),
            'in_review': ('info', 'قيد المراجعة'),
            'approved': ('success', 'تمت الموافقة'),
            'rejected': ('danger', 'مرفوض'),
            'in_progress': ('warning', 'قيد التنفيذ'),
            'done': ('success', 'مكتمل'),
            'canceled': ('secondary', 'ملغي'),
        }
        color, label = status_colors.get(obj.status, ('secondary', obj.status))
        return format_html(
            '<span class="badge bg-{}">{}</span>', 
            color, label
        )
    status_badge.short_description = 'الحالة'

    def contact_info(self, obj):
        info = []
        if obj.contact_phone:
            info.append(f'📞 {obj.contact_phone}')
        if obj.contact_email:
            info.append(f'✉️ {obj.contact_email}')
        return mark_safe('<br>'.join(info)) if info else '-'
    contact_info.short_description = 'التواصل'

    actions = [
        'mark_in_review', 'mark_approved', 'mark_rejected',
        'mark_in_progress', 'mark_done', 'mark_canceled'
    ]

    def _update_status(self, request, queryset, new_status):
        """تحديث حالة الطلبات المحددة"""
        updated = 0
        for req in queryset:
            old_status = req.status
            if old_status != new_status:
                req.update_status(new_status, request.user, f'تم التحديث من لوحة الإدارة')
                updated += 1
        return updated

    @admin.action(description='تحويل إلى: قيد المراجعة')
    def mark_in_review(self, request, queryset):
        updated = self._update_status(request, queryset, 'in_review')
        self.message_user(request, f'تم تحديث {updated} طلب إلى قيد المراجعة.')

    @admin.action(description='تحويل إلى: تمت الموافقة')
    def mark_approved(self, request, queryset):
        updated = self._update_status(request, queryset, 'approved')
        self.message_user(request, f'تم تحديث {updated} طلب إلى تمت الموافقة.')

    @admin.action(description='تحويل إلى: مرفوض')
    def mark_rejected(self, request, queryset):
        updated = self._update_status(request, queryset, 'rejected')
        self.message_user(request, f'تم تحديث {updated} طلب إلى مرفوض.')

    @admin.action(description='تحويل إلى: قيد التنفيذ')
    def mark_in_progress(self, request, queryset):
        updated = self._update_status(request, queryset, 'in_progress')
        self.message_user(request, f'تم تحديث {updated} طلب إلى قيد التنفيذ.')

    @admin.action(description='تحويل إلى: مكتمل')
    def mark_done(self, request, queryset):
        updated = self._update_status(request, queryset, 'done')
        self.message_user(request, f'تم تحديث {updated} طلب إلى مكتمل.')

    @admin.action(description='تحويل إلى: ملغي')
    def mark_canceled(self, request, queryset):
        updated = self._update_status(request, queryset, 'canceled')
        self.message_user(request, f'تم تحديث {updated} طلب إلى ملغي.')

    def save_model(self, request, obj, form, change):
        """تسجيل تغيير الحالة عند الحفظ"""
        if change:
            old_obj = ServiceRequest.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                # سيتم إنشاء StatusHistory بعد الحفظ
                super().save_model(request, obj, form, change)
                StatusHistory.objects.create(
                    request=obj,
                    from_status=old_obj.status,
                    to_status=obj.status,
                    changed_by=request.user,
                    notes='تم التحديث من لوحة الإدارة'
                )
                return
        super().save_model(request, obj, form, change)


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    """إدارة سجل تغييرات الحالات"""
    list_display = ['request_link', 'from_status_display', 'arrow', 'to_status_display', 'changed_by', 'created_at']
    list_filter = ['to_status', 'created_at']
    search_fields = ['request__id', 'changed_by__username', 'notes']
    readonly_fields = ['request', 'from_status', 'to_status', 'changed_by', 'created_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def request_link(self, obj):
        url = reverse('admin:requests_servicerequest_change', args=[obj.request.pk])
        return format_html('<a href="{}">طلب #{}</a>', url, obj.request.pk)
    request_link.short_description = 'الطلب'

    def from_status_display(self, obj):
        return obj.get_from_status_display()
    from_status_display.short_description = 'من'

    def to_status_display(self, obj):
        return obj.get_to_status_display()
    to_status_display.short_description = 'إلى'

    def arrow(self, obj):
        return format_html('<span style="font-size: 1.2em;">←</span>')
    arrow.short_description = ''


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """إدارة الإشعارات"""
    list_display = ['title', 'user', 'notification_type', 'is_read_badge', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    autocomplete_fields = ['user']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html('<span class="badge bg-secondary">مقروء</span>')
        return format_html('<span class="badge bg-primary">جديد</span>')
    is_read_badge.short_description = 'الحالة'

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description='تحديد كمقروء')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'تم تحديد {updated} إشعار كمقروء.')

    @admin.action(description='تحديد كغير مقروء')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'تم تحديد {updated} إشعار كغير مقروء.')
