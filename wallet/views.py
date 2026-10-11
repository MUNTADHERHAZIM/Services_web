"""
Wallet Views - عروض المحفظة والمعاملات المالية وإدارة شحن وسحب الرصيد باحترافية وأمان
"""

import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction

from core.utils import log_action
from requests.models import Notification, ServiceRequest
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, Http404
from django.db.models import Q
from .models import Wallet, Transaction, DepositMethod, DepositRequest, WithdrawalRequest, Receipt
from .forms import DepositRequestForm, WithdrawalRequestForm


@login_required
def my_wallet_view(request):
    """
    عرض لوحة المحفظة المالية الشاملة:
    - الأرصدة (المتاح، المعلق، إجمالي الأرباح، إجمالي السحوبات)
    - سجل المعاملات المالية المكتملة والمعلقة
    - طلبات شحن الرصيد المالي وإشعارات التحويل
    - طلبات سحب الأرباح والحسابات
    - وسائل الدفع والشحن المفعلة
    """
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    # وسائل الشحن النشطة في المنصة
    deposit_methods = DepositMethod.objects.filter(is_active=True).order_by('display_order', 'id')

    # طلبات الشحن الخاصة بالمستخدم
    deposit_requests = wallet.deposit_requests.select_related('deposit_method').order_by('-created_at')[:30]

    # طلبات السحب الخاصة بالمستخدم
    withdrawal_requests = wallet.withdrawal_requests.order_by('-created_at')[:30]

    # سجل المعاملات المالية
    transactions = wallet.transactions.select_related('related_order').order_by('-created_at')[:50]

    # إحصائيات سريعة للطلبات المعلقة
    pending_deposits_count = wallet.deposit_requests.filter(status=DepositRequest.Status.PENDING).count()
    pending_withdrawals_count = wallet.withdrawal_requests.filter(status=WithdrawalRequest.Status.PENDING).count()

    # النماذج
    deposit_form = DepositRequestForm()
    withdrawal_form = WithdrawalRequestForm(wallet=wallet)

    context = {
        'wallet': wallet,
        'deposit_methods': deposit_methods,
        'deposit_requests': deposit_requests,
        'withdrawal_requests': withdrawal_requests,
        'transactions': transactions,
        'pending_deposits_count': pending_deposits_count,
        'pending_withdrawals_count': pending_withdrawals_count,
        'deposit_form': deposit_form,
        'withdrawal_form': withdrawal_form,
    }

    return render(request, 'wallet/my_wallet.html', context)


@login_required
@require_POST
def create_deposit_request_view(request):
    """
    تقديم طلب شحن رصيد وإرفاق وصل التحويل المالي للمراجعة والتدقيق من قبل السوبر أدمن
    """
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    form = DepositRequestForm(request.POST, request.FILES)

    if form.is_valid():
        try:
            with transaction.atomic():
                deposit_req = form.save(commit=False)
                deposit_req.wallet = wallet
                deposit_req.reference_id = f"DEP-{uuid.uuid4().hex[:8].upper()}"
                deposit_req.status = DepositRequest.Status.PENDING
                deposit_req.save()

                # تسجيل معاملة مالية بحالة معلقة في سجل المعاملات
                method_name = deposit_req.deposit_method.name if deposit_req.deposit_method else "تحويل يدوي"
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type=Transaction.TransactionType.DEPOSIT,
                    amount=deposit_req.amount,
                    status=Transaction.TransactionStatus.PENDING,
                    description=f"طلب شحن رصيد قيد المراجعة والتدقيق عبر {method_name} - إشعار #{deposit_req.transaction_reference}",
                    reference_id=deposit_req.reference_id
                )

            # إشعار مدراء النظام (Staff / Superadmins) فوراً
            admin_users = User.objects.filter(is_staff=True)
            admin_link = reverse('admin:wallet_depositrequest_change', args=[deposit_req.pk])
            for admin_u in admin_users:
                Notification.objects.create(
                    user=admin_u,
                    notification_type=Notification.NotificationType.SYSTEM,
                    title=f"📥 طلب شحن رصيد جديد (${deposit_req.amount})",
                    message=f"قام العميل {request.user.username} بتقديم طلب شحن رصيد بمبلغ ${deposit_req.amount} عبر {method_name}. يرجى تدقيق الوصل وتأكيد الإيداع.",
                    link=admin_link
                )

            # توثيق في سجل التدقيق الأمني
            try:
                log_action(
                    user=request.user,
                    action_type='wallet',
                    description=f"تقديم طلب شحن رصيد #{deposit_req.reference_id} بمبلغ ${deposit_req.amount} عبر {method_name}",
                    request=request
                )
            except Exception:
                pass

            messages.success(
                request,
                f"🎉 تم استلام طلب شحن رصيدك بنجاح برقم مرجعي #{deposit_req.reference_id}! "
                f"يقوم فريق الإدارة المالية حالياً بمراجعة وتأكيد الحوالة، وسيتم شحن الرصيد في محفظتك فوراً."
            )
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء حفظ طلب الشحن: {str(e)}")
    else:
        # استخراج أول خطأ واضح للمستخدم
        error_msgs = []
        for field, errors in form.errors.items():
            for error in errors:
                error_msgs.append(error)
        joined_errors = " | ".join(error_msgs) if error_msgs else "يرجى التحقق من صحة البيانات والملفات المرفوعة."
        messages.error(request, f"تعذر إرسال طلب الشحن: {joined_errors}")

    return redirect('wallet:my_wallet')


@login_required
@require_POST
def create_withdrawal_request_view(request):
    """
    تقديم طلب سحب رصيد مع تجميد المبلغ أمنياً وبشكل ذري لمنع التضارب
    """
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    form = WithdrawalRequestForm(wallet=wallet, data=request.POST)

    if form.is_valid():
        amount = form.cleaned_data['amount']
        method = form.cleaned_data['method']
        account_info = form.get_account_info_dict()

        try:
            with transaction.atomic():
                # قفل أمني للمحفظة للتحقق من الرصيد وتجميده
                wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

                if amount > wallet.available_balance:
                    messages.error(request, f"عذراً، الرصيد المتاح في محفظتك (${wallet.available_balance}) غير كافٍ لإتمام طلب السحب.")
                    return redirect('wallet:my_wallet')

                # تجميد المبلغ المطلوب حتى تقوم الإدارة بالتحويل الفعلي
                wallet.frozen_balance += amount
                wallet.save(update_fields=['frozen_balance', 'updated_at'])

                # إنشاء طلب السحب
                withdrawal_req = WithdrawalRequest.objects.create(
                    wallet=wallet,
                    amount=amount,
                    method=method,
                    account_info=account_info,
                    status=WithdrawalRequest.Status.PENDING
                )

                # تسجيل معاملة مالية معلقة
                ref_code = f"WTH-{withdrawal_req.pk:05d}"
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type=Transaction.TransactionType.WITHDRAWAL,
                    amount=amount,
                    status=Transaction.TransactionStatus.PENDING,
                    description=f"طلب سحب رصيد قيد المعالجة ({withdrawal_req.get_method_display()})",
                    reference_id=ref_code
                )

            # إشعار الإدارة
            admin_users = User.objects.filter(is_staff=True)
            admin_link = reverse('admin:wallet_withdrawalrequest_change', args=[withdrawal_req.pk])
            for admin_u in admin_users:
                Notification.objects.create(
                    user=admin_u,
                    notification_type=Notification.NotificationType.SYSTEM,
                    title=f"💸 طلب سحب رصيد جديد (${amount})",
                    message=f"طلب المستخدم {request.user.username} سحب رصيد بمبلغ ${amount} عبر {withdrawal_req.get_method_display()}.",
                    link=admin_link
                )

            # توثيق في سجل التدقيق
            try:
                log_action(
                    user=request.user,
                    action_type='wallet',
                    description=f"تقديم طلب سحب رصيد #{ref_code} بمبلغ ${amount} عبر {withdrawal_req.get_method_display()}",
                    request=request
                )
            except Exception:
                pass

            messages.success(
                request,
                f"✅ تم تقديم طلب السحب بنجاح بمبلغ ${amount} برقم #{ref_code}. "
                f"تم حجز المبلغ مؤقتاً وسيقوم فريق الإدارة المالية بإرسال الحوالة إلى حسابك خلال 24 إلى 48 ساعة عمل."
            )
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء معالجة طلب السحب: {str(e)}")
    else:
        error_msgs = []
        for field, errors in form.errors.items():
            for error in errors:
                error_msgs.append(error)
        joined_errors = " | ".join(error_msgs) if error_msgs else "يرجى التحقق من صحة البيانات المدخلة."
        messages.error(request, f"تعذر تقديم طلب السحب: {joined_errors}")

    return redirect('wallet:my_wallet')


@login_required
@require_POST
def cancel_deposit_request_view(request, pk):
    """
    إلغاء طلب شحن الرصيد المعلق من قبل العميل نفسه
    """
    deposit_req = get_object_or_404(DepositRequest, pk=pk, wallet__user=request.user)

    if deposit_req.status != DepositRequest.Status.PENDING:
        messages.warning(request, "لا يمكن إلغاء هذا الطلب لأنه تمت مراجعته أو البت فيه مسبقاً.")
        return redirect('wallet:my_wallet')

    try:
        with transaction.atomic():
            deposit_req.status = DepositRequest.Status.REJECTED
            deposit_req.admin_notes = "تم إلغاء الطلب من قبل العميل."
            deposit_req.save(update_fields=['status', 'admin_notes'])

            Transaction.objects.filter(
                wallet=deposit_req.wallet,
                reference_id=deposit_req.reference_id,
                status=Transaction.TransactionStatus.PENDING
            ).update(status=Transaction.TransactionStatus.CANCELED)

        try:
            log_action(
                user=request.user,
                action_type='wallet',
                description=f"إلغاء طلب شحن الرصيد #{deposit_req.reference_id} من قبل المستخدم",
                request=request
            )
        except Exception:
            pass

        messages.info(request, f"تم إلغاء طلب شحن الرصيد #{deposit_req.reference_id} بنجاح.")
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء إلغاء الطلب: {str(e)}")

    return redirect('wallet:my_wallet')


@login_required
@require_POST
def cancel_withdrawal_request_view(request, pk):
    """
    إلغاء طلب سحب الرصيد المعلق من قبل العميل وإلغاء تجميد المبلغ فوراً ليعود لرصيده المتاح
    """
    withdrawal_req = get_object_or_404(WithdrawalRequest, pk=pk, wallet__user=request.user)

    if withdrawal_req.status != WithdrawalRequest.Status.PENDING:
        messages.warning(request, "لا يمكن إلغاء هذا الطلب لأنه قيد المعالجة أو تم تحويله بالفعل.")
        return redirect('wallet:my_wallet')

    try:
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=withdrawal_req.wallet_id)
            wallet.frozen_balance = max(Decimal('0'), wallet.frozen_balance - withdrawal_req.amount)
            wallet.save(update_fields=['frozen_balance', 'updated_at'])

            withdrawal_req.status = WithdrawalRequest.Status.REJECTED
            withdrawal_req.admin_notes = "تم إلغاء طلب السحب من قبل العميل واستعادة الرصيد."
            withdrawal_req.save(update_fields=['status', 'admin_notes'])

            ref_code = f"WTH-{withdrawal_req.pk:05d}"
            Transaction.objects.filter(
                wallet=wallet,
                reference_id=ref_code,
                status=Transaction.TransactionStatus.PENDING
            ).update(status=Transaction.TransactionStatus.CANCELED)

        try:
            log_action(
                user=request.user,
                action_type='wallet',
                description=f"إلغاء طلب السحب #{ref_code} واستعادة رصيد ${withdrawal_req.amount} للمحفظة",
                request=request
            )
        except Exception:
            pass

        messages.success(request, f"تم إلغاء طلب السحب بنجاح، وتمت إعادة مبلغ ${withdrawal_req.amount} إلى رصيدك المتاح فوراً.")
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء إلغاء طلب السحب: {str(e)}")

    return redirect('wallet:my_wallet')


@login_required
def deposit_method_info_api(request, pk):
    """
    واجهة برمجية سريعة لجلب بيانات وسيلة الشحن ديناميكياً لتحديث نافذة الدفع الفورية
    """
    method = get_object_or_404(DepositMethod, pk=pk, is_active=True)
    return JsonResponse({
        'id': method.id,
        'name': method.name,
        'account_name': method.account_name,
        'account_number': method.account_number,
        'instructions': method.instructions,
        'min_amount': str(method.min_amount),
        'max_amount': str(method.max_amount),
        'icon_class': method.icon_class,
    })


@login_required
def my_receipts_view(request):
    """
    سجل الفواتير والوصولات الرسمية المعتمدة للمستخدم:
    - وصولات طلبات الخدمات
    - وصولات شحن الرصيد
    - سندات سحب الأرباح
    - معاملات التحويل والاسترداد
    """
    receipts_qs = Receipt.objects.filter(
        Q(user=request.user) | Q(counterpart_user=request.user)
    ).select_related('user', 'counterpart_user').order_by('-issued_at', '-id')

    # تصفية حسب النوع
    current_type = request.GET.get('type', '').strip()
    if current_type in [choice[0] for choice in Receipt.ReceiptType.choices]:
        receipts_qs = receipts_qs.filter(receipt_type=current_type)

    # بحث بالرقم أو العنوان
    q = request.GET.get('q', '').strip()
    if q:
        receipts_qs = receipts_qs.filter(
            Q(receipt_number__icontains=q) |
            Q(title__icontains=q) |
            Q(payment_reference__icontains=q)
        )

    # تصفية حسب الحالة
    current_status = request.GET.get('status', '').strip()
    if current_status in [choice[0] for choice in Receipt.Status.choices]:
        receipts_qs = receipts_qs.filter(status=current_status)

    paginator = Paginator(receipts_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # إحصائيات للمستخدم
    user_receipts = Receipt.objects.filter(user=request.user, status=Receipt.Status.COMPLETED)
    total_orders_spent = sum((r.total_amount for r in user_receipts if r.receipt_type == Receipt.ReceiptType.ORDER), Decimal('0.00'))
    total_deposits = sum((r.total_amount for r in user_receipts if r.receipt_type == Receipt.ReceiptType.DEPOSIT), Decimal('0.00'))
    total_withdrawals = sum((r.total_amount for r in user_receipts if r.receipt_type == Receipt.ReceiptType.WITHDRAWAL), Decimal('0.00'))

    context = {
        'page_obj': page_obj,
        'receipts': page_obj.object_list,
        'current_type': current_type,
        'current_status': current_status,
        'q': q,
        'type_choices': Receipt.ReceiptType.choices,
        'status_choices': Receipt.Status.choices,
        'total_orders_spent': total_orders_spent,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
    }
    return render(request, 'wallet/receipt_list.html', context)


def receipt_detail_view(request, receipt_number):
    """
    استعراض الوصل المالي والفاتورة الرسمية بتصميم احترافي فائق الدقة
    متاح للمالك، أو الطرف الثاني، أو موظفي ومدراء النظام
    """
    receipt = get_object_or_404(
        Receipt.objects.select_related('user', 'counterpart_user', 'service_request', 'deposit_request', 'withdrawal_request'),
        receipt_number=receipt_number
    )

    is_owner = request.user.is_authenticated and (receipt.user == request.user or receipt.counterpart_user == request.user)
    is_admin = request.user.is_authenticated and request.user.is_staff

    if not (is_owner or is_admin):
        token_param = request.GET.get('token')
        if not token_param or str(receipt.verification_token) != token_param:
            return HttpResponseForbidden("عذراً، هذا الوصل المالي محمي وخاص بصاحب الحساب وإدارة النظام.")

    full_verify_url = request.build_absolute_uri(reverse('wallet:receipt_verify', args=[receipt.verification_token]))
    if not receipt.qr_code_svg:
        receipt.qr_code_svg = receipt.generate_qr_code_svg(base_url=request.build_absolute_uri('/'))
        receipt.save(update_fields=['qr_code_svg'])

    context = {
        'receipt': receipt,
        'full_verify_url': full_verify_url,
        'is_admin': is_admin,
    }
    return render(request, 'wallet/receipt_detail.html', context)


def receipt_verify_view(request, token):
    """
    صفحة التحقق الرقمية العامة من صحة الوصل المالي عبر مسح QR Code
    """
    receipt = get_object_or_404(
        Receipt.objects.select_related('user', 'counterpart_user'),
        verification_token=token
    )

    context = {
        'receipt': receipt,
        'is_verified': True,
    }
    return render(request, 'wallet/receipt_verify.html', context)


@login_required
def request_receipt_view(request, pk):
    """
    توجيه سريع أو إنشاء تلقائي لوصل طلب خدمة معين
    """
    service_req = get_object_or_404(
        ServiceRequest.objects.select_related('customer', 'service', 'service__provider', 'service__provider__user'),
        pk=pk
    )

    is_customer = service_req.customer == request.user
    is_provider = service_req.service.provider.user == request.user if hasattr(service_req.service, 'provider') and service_req.service.provider else False
    is_admin = request.user.is_staff

    if not (is_customer or is_provider or is_admin):
        return HttpResponseForbidden("لا تملك صلاحية استعراض فاتورة هذا الطلب.")

    receipt = Receipt.create_or_get_for_request(service_req, base_url=request.build_absolute_uri('/'))
    return redirect('wallet:receipt_detail', receipt_number=receipt.receipt_number)


@login_required
def deposit_receipt_view(request, pk):
    """
    توجيه سريع أو إنشاء تلقائي لوصل طلب شحن رصيد معين
    """
    deposit_req = get_object_or_404(DepositRequest.objects.select_related('wallet__user', 'deposit_method'), pk=pk)

    if deposit_req.wallet.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("لا تملك صلاحية استعراض هذا الوصل.")

    receipt = Receipt.create_or_get_for_deposit(deposit_req, base_url=request.build_absolute_uri('/'))
    return redirect('wallet:receipt_detail', receipt_number=receipt.receipt_number)


@login_required
def withdrawal_receipt_view(request, pk):
    """
    توجيه سريع أو إنشاء تلقائي لسند سحب أرباح معين
    """
    withdrawal_req = get_object_or_404(WithdrawalRequest.objects.select_related('wallet__user'), pk=pk)

    if withdrawal_req.wallet.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("لا تملك صلاحية استعراض هذا السند.")

    receipt = Receipt.create_or_get_for_withdrawal(withdrawal_req, base_url=request.build_absolute_uri('/'))
    return redirect('wallet:receipt_detail', receipt_number=receipt.receipt_number)


@login_required
def transaction_receipt_view(request, pk):
    """
    توجيه سريع لوصل أي معاملة مالية في المحفظة
    """
    txn = get_object_or_404(Transaction.objects.select_related('wallet__user', 'related_order'), pk=pk)

    if txn.wallet.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("لا تملك صلاحية استعراض وصل هذه المعاملة.")

    receipt = Receipt.create_or_get_for_transaction(txn, base_url=request.build_absolute_uri('/'))
    return redirect('wallet:receipt_detail', receipt_number=receipt.receipt_number)
