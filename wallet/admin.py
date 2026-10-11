"""
Wallet Admin - لوحة إدارة المحفظة والعمليات المالية والتحويلات البنكية المتقدمة
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from .models import Wallet, Transaction, WithdrawalRequest, DepositMethod, DepositRequest, Receipt


@admin.register(DepositMethod)
class DepositMethodAdmin(admin.ModelAdmin):
    """إدارة وسائل الدفع والشحن في المنصة"""
    list_display = (
        'name',
        'account_name',
        'account_number',
        'limits_display',
        'is_active',
        'display_order',
        'icon_preview',
        'created_at',
    )
    list_display_links = ('name',)
    list_editable = ('display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'account_name', 'account_number')
    ordering = ('display_order', 'id')

    fieldsets = (
        ('معلومات وسيلة الدفع الأساسية', {
            'fields': ('name', 'icon_class', 'account_name', 'account_number')
        }),
        ('الحدود والتعليمات', {
            'fields': ('min_amount', 'max_amount', 'instructions'),
            'description': 'حدد الحد الأدنى والأقصى لشحن الرصيد والتعليمات التي ستظهر للعميل أثناء التحويل.'
        }),
        ('حالة التفعيل والترتيب', {
            'fields': ('is_active', 'display_order')
        }),
    )

    def limits_display(self, obj):
        return f"${obj.min_amount} - ${obj.max_amount}"
    limits_display.short_description = 'حدود الشحن ($)'

    def icon_preview(self, obj):
        return format_html('<i class="bi {}" style="font-size: 1.3rem;"></i>', obj.icon_class or 'bi-phone')
    icon_preview.short_description = 'الأيقونة'


@admin.register(DepositRequest)
class DepositRequestAdmin(admin.ModelAdmin):
    """إدارة وتدقيق طلبات شحن الرصيد"""
    list_display = (
        'reference_id',
        'user_link',
        'amount_display',
        'deposit_method',
        'sender_name',
        'sender_phone',
        'transaction_reference',
        'receipt_thumbnail',
        'status_badge',
        'created_at',
        'admin_actions_column',
    )
    list_filter = ('status', 'deposit_method', 'created_at')
    search_fields = (
        'reference_id',
        'wallet__user__username',
        'wallet__user__first_name',
        'wallet__user__last_name',
        'sender_name',
        'sender_phone',
        'transaction_reference',
    )
    readonly_fields = (
        'reference_id',
        'wallet',
        'deposit_method',
        'amount',
        'sender_name',
        'sender_phone',
        'transaction_reference',
        'receipt_large_preview',
        'created_at',
        'reviewed_at',
        'reviewed_by',
    )
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('معلومات الطلب والمبلغ', {
            'fields': ('reference_id', 'wallet', 'deposit_method', 'amount', 'status')
        }),
        ('بيانات المرسل والحوالة', {
            'fields': ('sender_name', 'sender_phone', 'transaction_reference')
        }),
        ('إشعار التحويل البنكي (وصل الإيداع)', {
            'fields': ('receipt_large_preview',),
            'description': 'انقر على الصورة لفتحها بالحجم الكامل والتحقق من تفاصيل الإشعار المالي.'
        }),
        ('تدقيق الإدارة والملاحظات', {
            'fields': ('admin_notes', 'reviewed_by', 'reviewed_at')
        }),
        ('معلومات النظام', {
            'fields': ('created_at',)
        }),
    )

    actions = ['approve_selected_deposits', 'reject_selected_deposits']

    def user_link(self, obj):
        user = obj.wallet.user
        url = reverse('admin:auth_user_change', args=[user.pk])
        full_name = user.get_full_name()
        display_text = f"{user.username} ({full_name})" if full_name else user.username
        return format_html('<a href="{}" style="font-weight: bold; text-decoration: none;">{}</a>', url, display_text)
    user_link.short_description = 'المستخدم'

    def amount_display(self, obj):
        return format_html('<strong style="color: #059669; font-size: 1.05rem;">+${:,.2f}</strong>', obj.amount)
    amount_display.short_description = 'المبلغ'

    def receipt_thumbnail(self, obj):
        if obj.receipt_image:
            return format_html(
                '<a href="{}" target="_blank" title="عرض الوصل الأصلي">'
                '<img src="{}" style="width: 48px; height: 48px; object-fit: cover; border-radius: 6px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">'
                '</a>',
                obj.receipt_image.url,
                obj.receipt_image.url
            )
        return format_html('<span style="color: #94a3b8;">بدون صورة</span>')
    receipt_thumbnail.short_description = 'وصل التحويل'

    def receipt_large_preview(self, obj):
        if obj.receipt_image:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 450px; max-height: 450px; border-radius: 12px; border: 2px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">'
                '</a>'
                '<p style="margin-top: 6px; font-size: 0.85rem; color: #64748b;">انقر على الصورة لفتحها بنافذة مستقلة بالحجم الكامل</p>'
                '</div>',
                obj.receipt_image.url,
                obj.receipt_image.url
            )
        return format_html('<span style="color: #94a3b8;">لا توجد صورة مرفوعة</span>')
    receipt_large_preview.short_description = 'معاينة الوصل'

    def status_badge(self, obj):
        if obj.status == DepositRequest.Status.APPROVED:
            return format_html('<span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8rem;"><i class="bi bi-check-circle-fill"></i> معتمد وشُحن</span>')
        elif obj.status == DepositRequest.Status.PENDING:
            return format_html('<span style="background: #f59e0b; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8rem;"><i class="bi bi-clock-history"></i> قيد التدقيق</span>')
        elif obj.status == DepositRequest.Status.REJECTED:
            return format_html('<span style="background: #ef4444; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8rem;"><i class="bi bi-x-circle-fill"></i> مرفوض</span>')
        return obj.get_status_display()
    status_badge.short_description = 'الحالة'

    def admin_actions_column(self, obj):
        if obj.status == DepositRequest.Status.PENDING:
            approve_url = reverse('admin:wallet_depositrequest_approve', args=[obj.pk])
            reject_url = reverse('admin:wallet_depositrequest_reject', args=[obj.pk])
            return format_html(
                '<div style="display: flex; gap: 6px; align-items: center;">'
                '<a href="{}" class="button" style="background: #059669; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: bold;">'
                '<i class="bi bi-check2"></i> قبول وشحن'
                '</a>'
                '<a href="{}" class="button" style="background: #dc2626; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: bold;">'
                '<i class="bi bi-x"></i> رفض'
                '</a>'
                '</div>',
                approve_url,
                reject_url
            )
        return format_html('<span style="color: #64748b; font-size: 0.8rem;">تمت المعالجة</span>')
    admin_actions_column.short_description = 'إجراءات فورية'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:request_id>/approve/', self.admin_site.admin_view(self.approve_single_deposit), name='wallet_depositrequest_approve'),
            path('<int:request_id>/reject/', self.admin_site.admin_view(self.reject_single_deposit), name='wallet_depositrequest_reject'),
        ]
        return custom_urls + urls

    def approve_single_deposit(self, request, request_id):
        deposit_req = get_object_or_404(DepositRequest, pk=request_id)
        if deposit_req.status != DepositRequest.Status.PENDING:
            messages.warning(request, f"الطلب #{deposit_req.reference_id} تمت معالجته مسبقاً.")
            return redirect('admin:wallet_depositrequest_changelist')

        try:
            deposit_req.approve(admin_user=request.user, admin_notes="تمت مراجعة الوصل وتأكيد استلام المبلغ.", request=request)
            messages.success(request, f"✅ تمت الموافقة بنجاح على الطلب #{deposit_req.reference_id} وشحن رصيد ${deposit_req.amount} لحساب {deposit_req.wallet.user.username}.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء معالجة الطلب: {str(e)}")

        return redirect('admin:wallet_depositrequest_changelist')

    def reject_single_deposit(self, request, request_id):
        deposit_req = get_object_or_404(DepositRequest, pk=request_id)
        if deposit_req.status != DepositRequest.Status.PENDING:
            messages.warning(request, f"الطلب #{deposit_req.reference_id} تمت معالجته مسبقاً.")
            return redirect('admin:wallet_depositrequest_changelist')

        if request.method == 'POST':
            reason = request.POST.get('reason', '').strip()
            if not reason:
                reason = "تعذر تأكيد استلام الحوالة من قبل الإدارة المالية."
            try:
                deposit_req.reject(admin_user=request.user, admin_notes=reason, request=request)
                messages.success(request, f"تم رفض طلب الشحن #{deposit_req.reference_id} وإشعار العميل.")
            except Exception as e:
                messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('admin:wallet_depositrequest_changelist')

        # عرض صفحة تأكيد الرفض مع كتابة السبب
        context = {
            'title': f'رفض طلب شحن الرصيد #{deposit_req.reference_id}',
            'deposit_req': deposit_req,
            'opts': self.model._meta,
        }
        return render(request, 'admin/wallet/deposit_reject_confirm.html', context)

    def approve_selected_deposits(self, request, queryset):
        success_count = 0
        for deposit in queryset.filter(status=DepositRequest.Status.PENDING):
            try:
                deposit.approve(admin_user=request.user, admin_notes="موافقة جماعية من إدارة النظام.", request=request)
                success_count += 1
            except Exception:
                pass
        self.message_user(request, f"تمت الموافقة وشحن الرصيد لـ {success_count} طلب شحن بنجاح.", messages.SUCCESS)
    approve_selected_deposits.short_description = "✅ الموافقة على الطلبات المحددة وشحن الرصيد فوراً"

    def reject_selected_deposits(self, request, queryset):
        rejected_count = 0
        for deposit in queryset.filter(status=DepositRequest.Status.PENDING):
            try:
                deposit.reject(admin_user=request.user, admin_notes="رفض جماعي من قبل الإدارة.", request=request)
                rejected_count += 1
            except Exception:
                pass
        self.message_user(request, f"تم رفض {rejected_count} طلب شحن وإلغاؤها بنجاح.", messages.WARNING)
    reject_selected_deposits.short_description = "❌ رفض الطلبات المحددة"


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    """إدارة طلبات سحب الأرباح والرصيد"""
    list_display = (
        'reference_code_display',
        'user_link',
        'wallet_balance_info',
        'amount_display',
        'method_badge',
        'account_summary',
        'status_badge',
        'created_at',
        'admin_actions_column',
    )
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('wallet__user__username', 'admin_notes')
    readonly_fields = ('wallet', 'amount', 'method', 'account_info_formatted', 'created_at', 'processed_at')
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('معلومات طلب السحب والمبلغ', {
            'fields': ('wallet', 'amount', 'method', 'status')
        }),
        ('بيانات الحساب ووسيلة الاستلام', {
            'fields': ('account_info_formatted',)
        }),
        ('معالجة الإدارة والتحويل المالي', {
            'fields': ('admin_notes', 'processed_at')
        }),
        ('معلومات النظام', {
            'fields': ('created_at',)
        }),
    )

    actions = ['approve_selected_withdrawals', 'reject_selected_withdrawals']

    def reference_code_display(self, obj):
        return f"WTH-{obj.pk:05d}"
    reference_code_display.short_description = 'رقم الطلب'

    def user_link(self, obj):
        user = obj.wallet.user
        url = reverse('admin:auth_user_change', args=[user.pk])
        full_name = user.get_full_name()
        display_text = f"{user.username} ({full_name})" if full_name else user.username
        return format_html('<a href="{}" style="font-weight: bold; text-decoration: none;">{}</a>', url, display_text)
    user_link.short_description = 'المستخدم'

    def wallet_balance_info(self, obj):
        w = obj.wallet
        return format_html(
            '<div style="font-size: 0.8rem;">'
            '<span>الرصيد: <strong>${:,.2f}</strong></span><br>'
            '<span style="color: #f59e0b;">المعلق: <strong>${:,.2f}</strong></span>'
            '</div>',
            w.balance,
            w.frozen_balance
        )
    wallet_balance_info.short_description = 'حالة محفظة العميل'

    def amount_display(self, obj):
        return format_html('<strong style="color: #dc2626; font-size: 1.05rem;">-${:,.2f}</strong>', obj.amount)
    amount_display.short_description = 'المبلغ المطلوب'

    def method_badge(self, obj):
        colors = {
            'zain_cash': '#7c3aed',
            'qi_card': '#0284c7',
            'western_union': '#d97706',
            'bank': '#059669',
            'wise': '#16a34a',
            'other': '#6b7280',
        }
        color = colors.get(obj.method, '#6b7280')
        return format_html('<span style="background: {}; color: white; padding: 3px 8px; border-radius: 8px; font-size: 0.75rem; font-weight: bold;">{}</span>', color, obj.get_method_display())
    method_badge.short_description = 'وسيلة السحب'

    def account_summary(self, obj):
        if not obj.account_info or not isinstance(obj.account_info, dict):
            return str(obj.account_info or '---')
        holder = obj.account_info.get('account_holder', '')
        number = obj.account_info.get('account_number', '')
        return format_html(
            '<span style="font-weight: 600;">{}</span><br><code style="font-size: 0.8rem; background: #f1f5f9; padding: 2px 4px; border-radius: 4px;">{}</code>',
            holder, number
        )
    account_summary.short_description = 'بيانات المستلم'

    def account_info_formatted(self, obj):
        if not obj.account_info or not isinstance(obj.account_info, dict):
            return str(obj.account_info)
        info = obj.account_info
        return format_html(
            '<div style="background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; font-size: 0.9rem;">'
            '<p><strong>اسم المستلم:</strong> {}</p>'
            '<p><strong>رقم الحساب / المحفظة:</strong> <code>{}</code></p>'
            '<p><strong>المصرف / الفرع:</strong> {}</p>'
            '<p><strong>ملاحظات العميل:</strong> {}</p>'
            '</div>',
            info.get('account_holder', '---'),
            info.get('account_number', '---'),
            info.get('bank_or_branch', '---'),
            info.get('notes', '---')
        )
    account_info_formatted.short_description = 'تفاصيل حساب المستلم الكاملة'

    def status_badge(self, obj):
        if obj.status == WithdrawalRequest.Status.COMPLETED:
            return format_html('<span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8rem;"><i class="bi bi-check-circle-fill"></i> تم التحويل بنجاح</span>')
        elif obj.status == WithdrawalRequest.Status.PENDING:
            return format_html('<span style="background: #f59e0b; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8rem;"><i class="bi bi-clock-history"></i> قيد المراجعة</span>')
        elif obj.status == WithdrawalRequest.Status.PROCESSING:
            return format_html('<span style="background: #0284c7; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8rem;"><i class="bi bi-arrow-repeat"></i> جاري التحويل</span>')
        elif obj.status == WithdrawalRequest.Status.REJECTED:
            return format_html('<span style="background: #ef4444; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 0.8rem;"><i class="bi bi-x-circle-fill"></i> مرفوض ومُعاد</span>')
        return obj.get_status_display()
    status_badge.short_description = 'الحالة'

    def admin_actions_column(self, obj):
        if obj.status in [WithdrawalRequest.Status.PENDING, WithdrawalRequest.Status.PROCESSING]:
            approve_url = reverse('admin:wallet_withdrawalrequest_approve', args=[obj.pk])
            reject_url = reverse('admin:wallet_withdrawalrequest_reject', args=[obj.pk])
            return format_html(
                '<div style="display: flex; gap: 6px; align-items: center;">'
                '<a href="{}" class="button" style="background: #059669; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: bold;">'
                '<i class="bi bi-check2"></i> تأكيد التحويل'
                '</a>'
                '<a href="{}" class="button" style="background: #dc2626; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: bold;">'
                '<i class="bi bi-x"></i> رفض وإعادة'
                '</a>'
                '</div>',
                approve_url,
                reject_url
            )
        return format_html('<span style="color: #64748b; font-size: 0.8rem;">تم البت فيه</span>')
    admin_actions_column.short_description = 'إجراءات فورية'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:request_id>/approve/', self.admin_site.admin_view(self.approve_single_withdrawal), name='wallet_withdrawalrequest_approve'),
            path('<int:request_id>/reject/', self.admin_site.admin_view(self.reject_single_withdrawal), name='wallet_withdrawalrequest_reject'),
        ]
        return custom_urls + urls

    def approve_single_withdrawal(self, request, request_id):
        withdrawal = get_object_or_404(WithdrawalRequest, pk=request_id)
        if withdrawal.status not in [WithdrawalRequest.Status.PENDING, WithdrawalRequest.Status.PROCESSING]:
            messages.warning(request, f"طلب السحب #{withdrawal.pk} تم البت فيه مسبقاً.")
            return redirect('admin:wallet_withdrawalrequest_changelist')

        try:
            withdrawal.approve(admin_user=request.user, admin_notes="تم إرسال الحوالة البنكية/الإلكترونية بنجاح.", request=request)
            messages.success(request, f"✅ تم تأكيد إرسال الحوالة بنجاح وإنهاء سحب ${withdrawal.amount} لحساب {withdrawal.wallet.user.username}.")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء معالجة السحب: {str(e)}")

        return redirect('admin:wallet_withdrawalrequest_changelist')

    def reject_single_withdrawal(self, request, request_id):
        withdrawal = get_object_or_404(WithdrawalRequest, pk=request_id)
        if withdrawal.status not in [WithdrawalRequest.Status.PENDING, WithdrawalRequest.Status.PROCESSING]:
            messages.warning(request, f"طلب السحب #{withdrawal.pk} تم البت فيه مسبقاً.")
            return redirect('admin:wallet_withdrawalrequest_changelist')

        if request.method == 'POST':
            reason = request.POST.get('reason', '').strip()
            if not reason:
                reason = "بيانات الحساب غير مطابقة أو تعذر إرسال الحوالة."
            try:
                withdrawal.reject(admin_user=request.user, admin_notes=reason, request=request)
                messages.success(request, f"تم إلغاء طلب السحب #{withdrawal.pk} وإعادة المبلغ (${withdrawal.amount}) إلى رصيد المستخدم المتاح فوراً.")
            except Exception as e:
                messages.error(request, f"حدث خطأ: {str(e)}")
            return redirect('admin:wallet_withdrawalrequest_changelist')

        context = {
            'title': f'رفض طلب السحب #{withdrawal.pk}',
            'withdrawal': withdrawal,
            'opts': self.model._meta,
        }
        return render(request, 'admin/wallet/withdrawal_reject_confirm.html', context)

    def approve_selected_withdrawals(self, request, queryset):
        success_count = 0
        for req_obj in queryset.filter(status__in=[WithdrawalRequest.Status.PENDING, WithdrawalRequest.Status.PROCESSING]):
            try:
                req_obj.approve(admin_user=request.user, admin_notes="موافقة جماعية من إدارة النظام.", request=request)
                success_count += 1
            except Exception:
                pass
        self.message_user(request, f"تم تأكيد وإكمال {success_count} طلب سحب بنجاح.", messages.SUCCESS)
    approve_selected_withdrawals.short_description = "✅ تأكيد إرسال الحوالة وإنهاء السحب للطلبات المحددة"

    def reject_selected_withdrawals(self, request, queryset):
        rejected_count = 0
        for req_obj in queryset.filter(status__in=[WithdrawalRequest.Status.PENDING, WithdrawalRequest.Status.PROCESSING]):
            try:
                req_obj.reject(admin_user=request.user, admin_notes="رفض جماعي وإعادة المبالغ للمحافظ.", request=request)
                rejected_count += 1
            except Exception:
                pass
        self.message_user(request, f"تم رفض {rejected_count} طلب سحب وإعادة مبالغها لأصحابها بنجاح.", messages.WARNING)
    reject_selected_withdrawals.short_description = "❌ رفض طلبات السحب المحددة وإعادة المبالغ للأرصدة"


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """إدارة محافظ المستخدمين والأرصدة"""
    list_display = (
        'user_link',
        'balance_display',
        'frozen_balance_display',
        'available_balance_display',
        'total_earned_display',
        'total_withdrawn_display',
        'is_active',
        'updated_at',
    )
    list_filter = ('is_active', 'currency')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('total_earned', 'total_withdrawn', 'created_at', 'updated_at')

    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}" style="font-weight: bold;">{}</a>', url, obj.user.username)
    user_link.short_description = 'المستخدم'

    def balance_display(self, obj):
        return format_html('<strong>${:,.2f}</strong>', obj.balance)
    balance_display.short_description = 'الرصيد الكلي'

    def frozen_balance_display(self, obj):
        if obj.frozen_balance > 0:
            return format_html('<span style="color: #f59e0b; font-weight: bold;">${:,.2f}</span>', obj.frozen_balance)
        return "$0.00"
    frozen_balance_display.short_description = 'الرصيد المعلق'

    def available_balance_display(self, obj):
        return format_html('<strong style="color: #059669; font-size: 1.05rem;">${:,.2f}</strong>', obj.available_balance)
    available_balance_display.short_description = 'الرصيد المتاح'

    def total_earned_display(self, obj):
        return f"${obj.total_earned:,.2f}"
    total_earned_display.short_description = 'إجمالي الأرباح'

    def total_withdrawn_display(self, obj):
        return f"${obj.total_withdrawn:,.2f}"
    total_withdrawn_display.short_description = 'إجمالي السحوبات'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """سجل المعاملات والحركات المالية"""
    list_display = (
        'reference_id',
        'user_link',
        'type_badge',
        'amount_display',
        'fee_display',
        'status_badge',
        'description_truncated',
        'created_at',
    )
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference_id', 'wallet__user__username', 'description')
    readonly_fields = (
        'wallet',
        'transaction_type',
        'amount',
        'fee',
        'status',
        'description',
        'reference_id',
        'related_order',
        'metadata',
        'created_at',
        'completed_at',
    )
    ordering = ('-created_at',)
    list_per_page = 30

    def user_link(self, obj):
        user = obj.wallet.user
        url = reverse('admin:auth_user_change', args=[user.pk])
        return format_html('<a href="{}">{}</a>', url, user.username)
    user_link.short_description = 'المستخدم'

    def type_badge(self, obj):
        badges = {
            'deposit': ('#10b981', 'إيداع'),
            'withdrawal': ('#ef4444', 'سحب'),
            'order_payment': ('#0284c7', 'دفع طلب'),
            'order_earning': ('#059669', 'أرباح طلب'),
            'refund': ('#8b5cf6', 'استرداد'),
            'fee': ('#64748b', 'رسوم'),
            'bonus': ('#f59e0b', 'مكافأة'),
            'transfer': ('#3b82f6', 'تحويل'),
        }
        color, text = badges.get(obj.transaction_type, ('#6b7280', obj.get_transaction_type_display()))
        return format_html('<span style="background: {}; color: white; padding: 2px 8px; border-radius: 8px; font-size: 0.75rem; font-weight: bold;">{}</span>', color, text)
    type_badge.short_description = 'النوع'

    def amount_display(self, obj):
        if obj.transaction_type in ['deposit', 'order_earning', 'refund', 'bonus']:
            return format_html('<span style="color: #059669; font-weight: bold;">+${:,.2f}</span>', obj.amount)
        return format_html('<span style="color: #dc2626; font-weight: bold;">-${:,.2f}</span>', obj.amount)
    amount_display.short_description = 'المبلغ'

    def fee_display(self, obj):
        return f"${obj.fee:,.2f}" if obj.fee else "—"
    fee_display.short_description = 'الرسوم'

    def status_badge(self, obj):
        colors = {
            'completed': ('#10b981', 'مكتمل'),
            'pending': ('#f59e0b', 'معلق'),
            'failed': ('#ef4444', 'فشل'),
            'canceled': ('#64748b', 'ملغي'),
        }
        color, text = colors.get(obj.status, ('#6b7280', obj.get_status_display()))
        return format_html('<span style="background: {}; color: white; padding: 2px 8px; border-radius: 8px; font-size: 0.75rem;">{}</span>', color, text)
    status_badge.short_description = 'الحالة'

    def description_truncated(self, obj):
        if not obj.description:
            return '—'
        return (obj.description[:45] + '...') if len(obj.description) > 45 else obj.description
    description_truncated.short_description = 'الوصف'


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    """إدارة وتدقيق الفواتير والوصولات المالية الرسمية المعتمدة"""
    list_display = (
        'receipt_number',
        'user_link',
        'receipt_type_badge',
        'title',
        'total_amount_display',
        'amount_iqd_display',
        'status_badge',
        'payment_method_name',
        'issued_at',
        'view_receipt_button',
    )
    list_filter = ('receipt_type', 'status', 'issued_at', 'currency')
    search_fields = (
        'receipt_number',
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'title',
        'payment_reference',
        'security_hash',
    )
    readonly_fields = (
        'receipt_number',
        'verification_token',
        'security_hash',
        'qr_preview',
        'amount_iqd',
        'issued_at',
        'created_at',
        'updated_at',
        'view_online_receipt',
    )
    ordering = ('-issued_at', '-id')
    list_per_page = 30

    fieldsets = (
        ('المعلومات الأساسية للوصل', {
            'fields': ('receipt_number', 'receipt_type', 'status', 'user', 'counterpart_user', 'title')
        }),
        ('الارتباطات بالنظام', {
            'fields': ('service_request', 'deposit_request', 'withdrawal_request', 'transaction')
        }),
        ('القيم المالية والعملات', {
            'fields': ('subtotal', 'discount_amount', 'tax_or_fee', 'total_amount', 'currency', 'exchange_rate', 'amount_iqd')
        }),
        ('بيانات الدفع والتحويل', {
            'fields': ('payment_method_name', 'payment_reference', 'notes')
        }),
        ('التوثيق والأمان الرقمي', {
            'fields': ('verification_token', 'security_hash', 'qr_preview', 'view_online_receipt', 'metadata')
        }),
        ('التواريخ', {
            'fields': ('issued_at', 'created_at', 'updated_at')
        }),
    )

    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user_id])
        return format_html('<a href="{}" style="font-weight: bold; text-decoration: none;">{}</a>', url, obj.user.username)
    user_link.short_description = 'العميل'

    def receipt_type_badge(self, obj):
        colors = {
            'order': '#3b82f6',
            'deposit': '#10b981',
            'withdrawal': '#ef4444',
            'refund': '#8b5cf6',
            'transfer': '#06b6d4',
            'general': '#64748b',
        }
        color = colors.get(obj.receipt_type, '#6b7280')
        return format_html('<span style="background: {}; color: white; padding: 3px 8px; border-radius: 8px; font-size: 0.75rem; font-weight: bold;">{}</span>', color, obj.get_receipt_type_display())
    receipt_type_badge.short_description = 'نوع الوصل'

    def total_amount_display(self, obj):
        return format_html('<strong style="color: #059669; font-size: 1rem;">${:,.2f}</strong>', obj.total_amount)
    total_amount_display.short_description = 'المبلغ الصافي'

    def amount_iqd_display(self, obj):
        return f"{obj.amount_iqd:,.0f} د.ع"
    amount_iqd_display.short_description = 'المعادل بالدينار'

    def status_badge(self, obj):
        if obj.status == Receipt.Status.COMPLETED:
            return format_html('<span style="background: #10b981; color: white; padding: 3px 8px; border-radius: 8px; font-size: 0.75rem; font-weight: bold;"><i class="bi bi-check-circle-fill"></i> معتمد</span>')
        elif obj.status == Receipt.Status.PENDING:
            return format_html('<span style="background: #f59e0b; color: white; padding: 3px 8px; border-radius: 8px; font-size: 0.75rem; font-weight: bold;"><i class="bi bi-clock"></i> قيد المعالجة</span>')
        return format_html('<span style="background: #ef4444; color: white; padding: 3px 8px; border-radius: 8px; font-size: 0.75rem; font-weight: bold;"><i class="bi bi-x-circle"></i> ملغي</span>')
    status_badge.short_description = 'الحالة'

    def view_receipt_button(self, obj):
        url = reverse('wallet:receipt_detail', args=[obj.receipt_number])
        return format_html(
            '<a href="{}" target="_blank" style="background: #2563eb; color: white; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: bold;">'
            '<i class="bi bi-printer"></i> معاينة وطباعة'
            '</a>',
            url
        )
    view_receipt_button.short_description = 'معاينة الوصل'

    def qr_preview(self, obj):
        if obj.qr_code_svg:
            return format_html('<div style="width: 140px; height: 140px; padding: 6px; background: white; border: 1px solid #cbd5e1; border-radius: 8px;">{}</div>', format_html(obj.qr_code_svg))
        return "لا يوجد كود QR"
    qr_preview.short_description = 'معاينة QR Code'

    def view_online_receipt(self, obj):
        url = reverse('wallet:receipt_detail', args=[obj.receipt_number])
        verify_url = reverse('wallet:receipt_verify', args=[obj.verification_token])
        return format_html(
            '<div style="display: flex; gap: 10px; align-items: center;">'
            '<a href="{}" target="_blank" class="button" style="background: #059669; color: white; font-weight: bold;"><i class="bi bi-receipt"></i> فتح صفحة الوصل والطباعة</a>'
            '<a href="{}" target="_blank" class="button" style="background: #0ea5e9; color: white; font-weight: bold;"><i class="bi bi-patch-check"></i> فتح صفحة التحقق الرقمي</a>'
            '</div>',
            url,
            verify_url
        )
    view_online_receipt.short_description = 'الروابط الرقمية'
