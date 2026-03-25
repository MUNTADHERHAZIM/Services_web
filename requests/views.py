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
from .forms import ServiceRequestForm, UpdateStatusForm
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

    def form_valid(self, form):
        form.instance.service = self.service
        form.instance.customer = self.request.user
        
        # حفظ الطلب
        response = super().form_valid(form)
        
        # إنشاء إشعار للمقدم
        Notification.objects.create(
            user=self.service.provider.user,
            notification_type='request_new',
            title='طلب خدمة جديد',
            message=f'تم تقديم طلب جديد على خدمة "{self.service.title}" من {self.request.user.username}',
            link=self.object.get_absolute_url()
        )
        
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
    إلغاء طلب الخدمة (للعميل فقط)
    """
    model = ServiceRequest
    fields = []
    template_name = 'requests/cancel_confirm.html'

    def test_func(self):
        obj = self.get_object()
        return (
            obj.customer == self.request.user and 
            obj.can_be_canceled()
        )

    def form_valid(self, form):
        self.object.update_status('canceled', self.request.user, 'تم الإلغاء بواسطة العميل')
        messages.success(self.request, 'تم إلغاء الطلب بنجاح.')
        return redirect('requests:my_requests')


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
