"""
Dashboard Views - عروض لوحة التحكم
"""

from django.views.generic import TemplateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from services.models import Category, Service, Tag
from requests.models import ServiceRequest
from accounts.models import Provider, UserProfile
from accounts.decorators import customer_required, provider_required, admin_required




class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    """توجيه المستخدم إلى لوحة التحكم المناسبة"""
    
    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect('accounts:profile')
        
        user_type = request.user.profile.user_type
        
        if user_type in ['customer', 'CUSTOMER']:
            return redirect('dashboard:customer')
        elif user_type in ['provider', 'PROVIDER']:
            return redirect('dashboard:provider')
        elif user_type in ['admin', 'ADMIN'] or request.user.is_staff:
            return redirect('dashboard:admin')
        else:
            return redirect('dashboard:customer')


@method_decorator(customer_required, name='dispatch')
class CustomerDashboardView(TemplateView):
    """لوحة تحكم العميل"""
    template_name = 'dashboard/customer_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['my_requests'] = ServiceRequest.objects.filter(
            customer=user
        ).order_by('-created_at')[:10]
        
        context['pending_requests'] = ServiceRequest.objects.filter(
            customer=user, status='new'
        ).count()
        
        context['in_progress_requests'] = ServiceRequest.objects.filter(
            customer=user, status='in_progress'
        ).count()
        
        context['completed_requests'] = ServiceRequest.objects.filter(
            customer=user, status='done'
        ).count()
        
        return context


@method_decorator(provider_required, name='dispatch')
class ProviderDashboardView(TemplateView):
    """لوحة تحكم مقدم الخدمة"""
    template_name = 'dashboard/provider_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # التأكد من وجود كائن المزود
        if not hasattr(user, 'provider_profile'):
            Provider.objects.get_or_create(
                user=user,
                defaults={
                    'display_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                    'bio': 'مقدم خدمة جديد'
                }
            )
        
        context['is_approved'] = user.profile.provider_approved
        
        context['my_services'] = Service.objects.filter(
            provider__user=user
        ).order_by('-created_at')[:6]
        
        context['services_count'] = Service.objects.filter(
            provider__user=user
        ).count()
        
        my_requests = ServiceRequest.objects.filter(
            service__provider__user=user
        ).order_by('-created_at')
        
        context['new_requests'] = my_requests.filter(status='new').count()
        context['in_progress'] = my_requests.filter(status='in_progress').count()
        context['completed'] = my_requests.filter(status='done').count()
        context['recent_requests'] = my_requests[:10]
        
        return context


@method_decorator(provider_required, name='dispatch')
class ProviderServiceListView(ListView):
    """قائمة خدمات المزود"""
    model = Service
    template_name = 'dashboard/provider_services.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        return Service.objects.filter(provider__user=self.request.user).order_by('-created_at')


@method_decorator(provider_required, name='dispatch')
class ProviderRequestListView(ListView):
    """قائمة الطلبات المستلمة للمزود"""
    model = ServiceRequest
    template_name = 'dashboard/provider_requests.html'
    context_object_name = 'service_requests'
    paginate_by = 15

    def get_queryset(self):
        return ServiceRequest.objects.filter(service__provider__user=self.request.user).order_by('-created_at')


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """مزيج للتحقق من صلاحيات الموظفين"""
    
    def test_func(self):
        return self.request.user.is_staff


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    """الصفحة الرئيسية للوحة التحكم"""
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إحصائيات عامة
        context['stats'] = {
            'services_count': Service.objects.filter(is_active=True).count(),
            'categories_count': Category.objects.filter(is_active=True).count(),
            'providers_count': Provider.objects.filter(is_active=True).count(),
            'requests_count': ServiceRequest.objects.count(),
        }
        
        # الطلبات حسب الحالة
        context['requests_by_status'] = ServiceRequest.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # الحالات بأسماء عربية
        status_names = dict(ServiceRequest.Status.choices)
        for item in context['requests_by_status']:
            item['status_display'] = status_names.get(item['status'], item['status'])
        
        # آخر الطلبات
        context['recent_requests'] = ServiceRequest.objects.select_related(
            'service', 'customer'
        ).order_by('-created_at')[:10]
        
        # أفضل الخدمات (الأكثر مشاهدة)
        context['top_services'] = Service.objects.filter(
            is_active=True
        ).order_by('-views_count')[:5]
        
        # الطلبات الجديدة التي تحتاج معالجة
        context['pending_requests'] = ServiceRequest.objects.filter(
            status__in=['new', 'in_review']
        ).count()
        
        return context


class ManageServicesView(StaffRequiredMixin, ListView):
    """إدارة الخدمات"""
    model = Service
    template_name = 'dashboard/manage_services.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_queryset(self):
        queryset = Service.objects.select_related('category', 'provider__user')
        
        # البحث
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(provider__display_name__icontains=search)
            )
        
        # فلترة بالتصنيف
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # فلترة بالحالة
        is_active = self.request.GET.get('is_active')
        if is_active == '1':
            queryset = queryset.filter(is_active=True)
        elif is_active == '0':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ToggleServiceActiveView(StaffRequiredMixin, UpdateView):
    """تفعيل/تعطيل خدمة"""
    model = Service
    fields = []
    
    def post(self, request, *args, **kwargs):
        service = self.get_object()
        service.is_active = not service.is_active
        service.save(update_fields=['is_active'])
        status = 'تفعيل' if service.is_active else 'تعطيل'
        messages.success(request, f'تم {status} الخدمة "{service.title}" بنجاح.')
        return redirect('dashboard:manage_services')


class ManageRequestsView(StaffRequiredMixin, ListView):
    """إدارة الطلبات"""
    model = ServiceRequest
    template_name = 'dashboard/manage_requests.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        queryset = ServiceRequest.objects.select_related(
            'service__category', 'customer'
        )
        
        # فلترة بالحالة
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # البحث
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(service__title__icontains=search) |
                Q(customer__username__icontains=search)
            )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ServiceRequest.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ManageCategoriesView(StaffRequiredMixin, ListView):
    """إدارة التصنيفات"""
    model = Category
    template_name = 'dashboard/manage_categories.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        return Category.objects.annotate(
            services_count=Count('services', filter=Q(services__is_active=True))
        ).order_by('order', 'name')


class ManageProvidersView(StaffRequiredMixin, ListView):
    """إدارة مقدمي الخدمات"""
    model = Provider
    template_name = 'dashboard/manage_providers.html'
    context_object_name = 'providers'
    paginate_by = 20

    def get_queryset(self):
        queryset = Provider.objects.select_related('user').annotate(
            services_count=Count('services', filter=Q(services__is_active=True))
        )
        
        # فلترة بالتوثيق
        is_verified = self.request.GET.get('is_verified')
        if is_verified == '1':
            queryset = queryset.filter(is_verified=True)
        elif is_verified == '0':
            queryset = queryset.filter(is_verified=False)
        
        return queryset.order_by('-created_at')


class ToggleProviderVerifiedView(StaffRequiredMixin, UpdateView):
    """توثيق/إلغاء توثيق مقدم خدمة"""
    model = Provider
    fields = []
    
    def post(self, request, *args, **kwargs):
        provider = self.get_object()
        provider.is_verified = not provider.is_verified
        provider.save(update_fields=['is_verified'])
        status = 'توثيق' if provider.is_verified else 'إلغاء توثيق'
        messages.success(request, f'تم {status} "{provider.display_name}" بنجاح.')
        return redirect('dashboard:manage_providers')
