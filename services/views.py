"""
Services Views - عروض الخدمات
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib import messages

from .models import Category, Tag, Service
from .forms import ServiceSearchForm, ServiceForm
from accounts.decorators import provider_required


class ServiceCreateView(LoginRequiredMixin, CreateView):
    """إنشاء خدمة جديدة"""
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('dashboard:provider')

    @method_decorator(provider_required)
    def dispatch(self, request, *args, **kwargs):
        # السماح للمزود بإضافة خدمة حتى لو لم يتم الموافقة عليه بعد (للتجربة)
        # إذا أردت تفعيل الموافقة الإجبارية، قم بإزالة التعليق عن الأسطر التالية:
        # if not request.user.profile.provider_approved:
        #     messages.error(request, 'يجب الموافقة على حسابك كمزود قبل إنشاء الخدمات.')
        #     return redirect('dashboard:provider')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.provider = self.request.user.provider_profile
        messages.success(self.request, 'تم إنشاء الخدمة بنجاح.')
        return super().form_valid(form)


class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    """تعديل خدمة موجودة"""
    model = Service
    form_class = ServiceForm
    template_name = 'services/service_form.html'
    success_url = reverse_lazy('dashboard:provider')

    @method_decorator(provider_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Service.objects.filter(provider__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'تم تعديل الخدمة بنجاح.')
        return super().form_valid(form)


class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    """حذف خدمة"""
    model = Service
    template_name = 'services/service_confirm_delete.html'
    success_url = reverse_lazy('dashboard:provider')

    @method_decorator(provider_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Service.objects.filter(provider__user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف الخدمة بنجاح.')
        return super().delete(request, *args, **kwargs)


class ServiceListView(ListView):
    """
    قائمة الخدمات مع البحث والفلترة
    """
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = getattr(settings, 'SERVICES_PER_PAGE', 12)

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).select_related(
            'category', 'provider__user'
        ).prefetch_related('tags')

        # البحث
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(summary__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        # فلترة بالتصنيف
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # فلترة بالوسم
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        # فلترة بالسعر
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        # فلترة بالتقييم
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(avg_rating__gte=rating)

        # الترتيب
        sort = self.request.GET.get('sort', '-created_at')
        sort_options = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'price_low': 'price',
            'price_high': '-price',
            'rating': '-avg_rating',
            'popular': '-views_count',
        }
        order_by = sort_options.get(sort, '-created_at')
        queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ServiceSearchForm(self.request.GET)
        context['categories'] = Category.objects.filter(is_active=True).order_by('order', 'name')
        context['tags'] = Tag.objects.all()[:20]
        context['current_category'] = self.request.GET.get('category', '')
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        context['search_query'] = self.request.GET.get('search', '')
        context['total_count'] = self.get_queryset().count()
        return context


class ServiceDetailView(DetailView):
    """
    تفاصيل الخدمة
    """
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Service.objects.filter(is_active=True).select_related(
            'category', 'provider__user'
        ).prefetch_related('tags', 'images', 'reviews__customer', 'features', 'packages', 'faqs', 'testimonials')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # زيادة عدد المشاهدات
        obj.increment_views()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object

        # خدمات مشابهة (من نفس التصنيف)
        context['related_services'] = Service.objects.filter(
            is_active=True,
            category=service.category
        ).exclude(pk=service.pk).select_related('category', 'provider__user')[:4]

        # خدمات أخرى من نفس المقدم
        context['provider_services'] = Service.objects.filter(
            is_active=True,
            provider=service.provider
        ).exclude(pk=service.pk).select_related('category')[:4]

        # التقييمات المعتمدة
        context['reviews'] = service.reviews.filter(is_approved=True).select_related('customer')[:10]

        # هل المستخدم طلب هذه الخدمة سابقاً؟
        if self.request.user.is_authenticated:
            context['user_has_requested'] = service.requests.filter(
                customer=self.request.user
            ).exists()
        
        return context


class CategoryDetailView(DetailView):
    """
    عرض تصنيف مع خدماته
    """
    model = Category
    template_name = 'services/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object

        # خدمات التصنيف مع pagination
        services = Service.objects.filter(
            is_active=True,
            category=category
        ).select_related('provider__user').prefetch_related('tags')

        # ترتيب
        sort = self.request.GET.get('sort', 'newest')
        sort_options = {
            'newest': '-created_at',
            'price_low': 'price',
            'price_high': '-price',
            'rating': '-avg_rating',
        }
        order_by = sort_options.get(sort, '-created_at')
        services = services.order_by(order_by)

        context['services'] = services
        context['services_count'] = services.count()
        context['current_sort'] = sort

        return context


class ProviderDetailView(DetailView):
    """
    عرض مقدم الخدمة مع خدماته
    """
    template_name = 'services/provider_detail.html'
    context_object_name = 'provider'

    def get_object(self):
        from accounts.models import Provider
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Provider, user__username=self.kwargs['username'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provider = self.object

        # خدمات المقدم
        context['services'] = Service.objects.filter(
            is_active=True,
            provider=provider
        ).select_related('category').prefetch_related('tags')

        context['services_count'] = context['services'].count()

        # معرض الأعمال
        from services.models import ProviderPortfolio
        context['portfolio_items'] = ProviderPortfolio.objects.filter(
            provider=provider
        ).order_by('-is_featured', 'order', '-created_at')[:6]

        return context


class TagServicesView(ListView):
    """
    خدمات وسم معين
    """
    model = Service
    template_name = 'services/tag_services.html'
    context_object_name = 'services'
    paginate_by = 12

    def get_queryset(self):
        from django.shortcuts import get_object_or_404
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Service.objects.filter(
            is_active=True,
            tags=self.tag
        ).select_related('category', 'provider__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context
