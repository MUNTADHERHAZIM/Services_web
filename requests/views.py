"""
Requests Views - عروض طلبات الخدمات
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from django.conf import settings
from django.db.models import Q

from .models import ServiceRequest, StatusHistory, Notification
from .forms import ServiceRequestForm, UpdateStatusForm, RequestCancelForm
from services.models import Service


class ServiceRequestCreateView(LoginRequiredMixin, CreateView):
    """
    إنشاء طلب خدمة جديد
    """
    model = ServiceRequest
    form_class = ServiceRequestForm
    template_name = 'requests/request_create.html'

    def dispatch(self, request, *args, **kwargs):
        # جلب الخدمة والتحقق من أنها نشطة
        self.service = get_object_or_404(
            Service, 
            slug=kwargs.get('service_slug'),
            is_active=True
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        return context

    def post(self, request, *args, **kwargs):
        # التحقق من الكابتشا الأمني
        from core.captcha import verify_captcha_response
        captcha_token = request.POST.get('captcha_token')
        captcha_code = request.POST.get('captcha_code')

        is_valid, err_msg = verify_captcha_response(captcha_token, captcha_code)
        if not is_valid:
            messages.error(request, err_msg)
            return self.get(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        from decimal import Decimal
        form.instance.service = self.service
        form.instance.customer = self.request.user

        base_price = self.service.price or Decimal('0')
        form.instance.price = base_price
        form.instance.discount_amount = Decimal('0')

        coupon_code = self.request.POST.get('coupon_code', '').strip().upper()
        if coupon_code:
            from core.models import Coupon
            coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
            if coupon:
                is_valid, _ = coupon.is_valid_for(base_price)
                if is_valid:
                    discount = coupon.calculate_discount(base_price)
                    form.instance.coupon = coupon
                    form.instance.discount_amount = discount
                    form.instance.price = max(Decimal('0'), base_price - discount)
                    coupon.used_count += 1
                    coupon.save(update_fields=['used_count'])
        
        # حفظ الطلب
        response = super().form_valid(form)
        
        # إنشاء الوصل والفاتورة المالية الرسمية وحفظها في النظام
        try:
            from wallet.models import Receipt
            Receipt.create_or_get_for_request(self.object)
        except Exception:
            pass

        # إنشاء إشعار للمقدم
        Notification.objects.create(
            user=self.service.provider.user,
            notification_type='request_new',
            title='طلب خدمة جديد',
            message=f'تم تقديم طلب جديد على خدمة "{self.service.title}" من {self.request.user.username}',
            link=self.object.get_absolute_url()
        )
        
        currency = getattr(self.service, 'currency', 'IQD')
        if form.instance.discount_amount > 0:
            if currency == 'USD':
                disc_str = f"${form.instance.discount_amount}"
            else:
                disc_str = f"{int(form.instance.discount_amount):,} د.ع"
            messages.success(self.request, f'تم تقديم طلبك بنجاح مع تطبيق خصم قدره {disc_str}!')
        else:
            messages.success(self.request, 'تم تقديم طلبك بنجاح! سيتم التواصل معك قريباً.')
        return response

    def get_success_url(self):
        return reverse('requests:my_requests')


class MyRequestsListView(LoginRequiredMixin, ListView):
    """
    قائمة طلبات المستخدم الحالي
    """
    model = ServiceRequest
    template_name = 'requests/my_requests.html'
    context_object_name = 'requests'
    paginate_by = getattr(settings, 'REQUESTS_PER_PAGE', 10)

    def get_queryset(self):
        queryset = ServiceRequest.objects.filter(
            customer=self.request.user
        ).select_related('service__category', 'service__provider__user')

        # فلترة بالحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ServiceRequest.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        return context


class RequestDetailView(LoginRequiredMixin, DetailView):
    """
    تفاصيل طلب خدمة
    """
    model = ServiceRequest
    template_name = 'requests/request_detail.html'
    context_object_name = 'request_obj'

    def get_queryset(self):
        # المستخدم يمكنه رؤية طلباته فقط، أو إذا كان staff/provider
        user = self.request.user
        if user.is_staff:
            return ServiceRequest.objects.all()
        
        # العميل أو مقدم الخدمة
        return ServiceRequest.objects.filter(
            Q(customer=user) | Q(service__provider__user=user)
        ).select_related('service__category', 'service__provider__user', 'customer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_history'] = self.object.status_history.select_related('changed_by').order_by('-created_at')
        
        # هل يمكن للمستخدم تحديث الحالة؟
        user = self.request.user
        context['can_update_status'] = (
            user.is_staff or 
            (hasattr(user, 'provider_profile') and 
             self.object.service.provider == user.provider_profile)
        )
        
        # هل يمكن للعميل إلغاء الطلب؟
        context['can_cancel'] = (
            self.object.customer == user and 
            self.object.can_be_canceled()
        )
        
        return context


class UpdateRequestStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    تحديث حالة الطلب (للموظفين ومقدمي الخدمات)
    """
    model = ServiceRequest
    form_class = UpdateStatusForm
    template_name = 'requests/update_status.html'

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        # السماح للـ staff أو لمقدم الخدمة
        if user.is_staff:
            return True
        if hasattr(user, 'provider_profile'):
            return obj.service.provider == user.provider_profile
        return False

    def form_valid(self, form):
        old_status = self.get_object().status
        new_status = form.cleaned_data['status']
        notes = form.cleaned_data.get('staff_notes', '')

        if old_status != new_status:
            # تحديث الحالة مع التسجيل
            self.object.update_status(new_status, self.request.user, notes)
            
            # إشعار العميل
            Notification.objects.create(
                user=self.object.customer,
                notification_type='request_status',
                title='تحديث حالة الطلب',
                message=f'تم تحديث حالة طلبك "{self.object.service.title}" إلى: {self.object.get_status_display()}',
                link=self.object.get_absolute_url()
            )
            
            messages.success(self.request, 'تم تحديث حالة الطلب بنجاح.')
        else:
            messages.info(self.request, 'لم يتم إجراء أي تغيير.')

        return redirect('requests:request_detail', pk=self.object.pk)


class CancelRequestView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    إلغاء طلب الخدمة مع تسجيل أسباب احترافية وإشعار الإدارة ومقدم الخدمة
    """
    model = ServiceRequest
    form_class = RequestCancelForm
    template_name = 'requests/cancel_confirm.html'

    def test_func(self):
        obj = self.get_object()
        return (
            (obj.customer == self.request.user or self.request.user.is_staff) and 
            obj.can_be_canceled()
        )

    def form_valid(self, form):
        reason = form.cleaned_data['cancellation_reason']
        notes = form.cleaned_data.get('cancellation_notes', '')
        
        self.object.cancel_order(
            reason=reason,
            notes=notes,
            canceled_by=self.request.user,
            request=self.request
        )
        messages.success(self.request, 'تم إلغاء الطلب بنجاح، وتم إرسال تفاصيل وأسباب الإلغاء لإدارة المنصة ومقدم الخدمة.')
        return redirect('requests:request_detail', pk=self.object.pk)


class NotificationsListView(LoginRequiredMixin, ListView):
    """
    قائمة إشعارات المستخدم
    """
    model = Notification
    template_name = 'requests/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


def mark_notification_read(request, pk):
    """تحديد إشعار كمقروء"""
    if request.user.is_authenticated:
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.mark_as_read()
        if notification.link:
            return redirect(notification.link)
    return redirect('requests:notifications')


def mark_all_notifications_read(request):
    """تحديد جميع الإشعارات كمقروءة"""
    if request.user.is_authenticated:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'تم تحديد جميع الإشعارات كمقروءة.')
    return redirect('requests:notifications')
