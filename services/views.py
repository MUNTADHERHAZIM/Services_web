"""
Services Views - عروض الخدمات
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db import models
from django.db.models import Q, F
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
        if not request.user.profile.provider_approved:
            messages.error(request, 'يجب الموافقة على حسابك كمزود قبل إنشاء الخدمات.')
            return redirect('dashboard:provider')
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

            # تسجيل البحث في التحليلات
            try:
                from analytics.models import SearchAnalytics
                
                results_count = queryset.count()
                obj, created = SearchAnalytics.objects.get_or_create(
                    query=search.lower(),
                    defaults={'search_count': 1, 'results_count_avg': results_count}
                )
                if not created:
                    total_searches = obj.search_count + 1
                    obj.results_count_avg = ((obj.results_count_avg * obj.search_count) + results_count) / total_searches
                    obj.search_count = total_searches
                    obj.save()
            except Exception:
                pass


        # فلترة بالتصنيف (يشمل التصنيف الرئيسي وفروعه)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(
                Q(category__slug=category) | Q(category__parent__slug=category)
            )

        # فلترة بالوسم
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        # توحيد العملات للمقارنة والفلترة والترتيب (1 دولار = 1500 دينار عراقي)
        queryset = queryset.annotate(
            price_in_iqd=models.Case(
                models.When(currency='USD', then=models.F('price') * 1500),
                default=models.F('price'),
                output_field=models.DecimalField(max_digits=14, decimal_places=2)
            )
        )

        user_curr = self.request.session.get('user_currency', 'IQD')

        # فلترة بالعملة
        currency_filter = self.request.GET.get('currency')
        if currency_filter in ['IQD', 'USD']:
            queryset = queryset.filter(currency=currency_filter)

        # فلترة بالسعر متناسبة مع العملة المعروضة
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            try:
                min_val = float(price_min)
                if user_curr == 'USD':
                    min_val = min_val * 1500
                queryset = queryset.filter(price_in_iqd__gte=min_val)
            except (ValueError, TypeError):
                pass
        if price_max:
            try:
                max_val = float(price_max)
                if user_curr == 'USD':
                    max_val = max_val * 1500
                queryset = queryset.filter(price_in_iqd__lte=max_val)
            except (ValueError, TypeError):
                pass

        # فلترة بالتقييم
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(avg_rating__gte=rating)

        # فلترة بالعروض الخاصة والصفقات المخفضة
        deals = self.request.GET.get('deals') or self.request.GET.get('discount')
        if deals in ['true', '1', 'yes']:
            queryset = queryset.filter(
                original_price__isnull=False,
                price__isnull=False,
                original_price__gt=F('price')
            )

        # الترتيب الموحد المتوافق مع الدينار والدولار
        sort = self.request.GET.get('sort', '-created_at')
        sort_options = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'price_low': 'price_in_iqd',
            'price_high': '-price_in_iqd',
            'rating': '-avg_rating',
            'popular': '-views_count',
        }
        order_by = sort_options.get(sort, '-created_at')
        queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ServiceSearchForm(self.request.GET)
        context['main_categories'] = Category.objects.filter(
            is_active=True, parent__isnull=True
        ).prefetch_related('subcategories').order_by('order', 'name')
        context['categories'] = Category.objects.filter(is_active=True).select_related('parent').order_by('order', 'name')
        context['tags'] = Tag.objects.all()[:20]
        
        current_slug = self.request.GET.get('category', '').strip()
        context['current_category'] = current_slug
        
        current_cat_obj = None
        if current_slug:
            current_cat_obj = Category.objects.filter(slug=current_slug).select_related('parent').first()
        context['current_category_obj'] = current_cat_obj
        
        if current_cat_obj:
            if current_cat_obj.parent:
                context['active_main_category'] = current_cat_obj.parent
                context['active_subcategories'] = current_cat_obj.parent.subcategories.filter(is_active=True).order_by('order', 'name')
            else:
                context['active_main_category'] = current_cat_obj
                context['active_subcategories'] = current_cat_obj.subcategories.filter(is_active=True).order_by('order', 'name')
        else:
            context['active_main_category'] = None
            context['active_subcategories'] = []

        context['current_sort'] = self.request.GET.get('sort', 'newest')
        context['search_query'] = self.request.GET.get('search', '')
        context['deals_only'] = self.request.GET.get('deals') in ['true', '1', 'yes']
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
        
        # تسجيل مشاهدة الخدمة في التحليلات
        try:
            from analytics.models import ServiceView
            
            # تحديد نوع الجهاز من الـ user agent
            user_agent = self.request.META.get('HTTP_USER_AGENT', '').lower()
            device_type = 'desktop'
            if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                device_type = 'mobile'
            elif 'ipad' in user_agent or 'tablet' in user_agent:
                device_type = 'tablet'
                
            # الحصول على عنوان IP
            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = self.request.META.get('REMOTE_ADDR')
                
            referrer = self.request.META.get('HTTP_REFERER', '')
            
            # تسجيل المشاهدة
            ServiceView.objects.create(
                service=obj,
                user=self.request.user if self.request.user.is_authenticated else None,
                ip_address=ip_address,
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500],
                referrer=referrer[:200],
                device_type=device_type
            )
        except Exception:
            pass
            
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

        # خدمات التصنيف (تشمل خدمات التصنيفات الفرعية إذا كان قسماً رئيسياً) مع الترتيب
        if category.is_main_category:
            services = Service.objects.filter(
                is_active=True
            ).filter(
                Q(category=category) | Q(category__parent=category)
            ).select_related('category', 'provider__user').prefetch_related('tags')
        else:
            services = Service.objects.filter(
                is_active=True,
                category=category
            ).select_related('category', 'provider__user').prefetch_related('tags')

        # توحيد العملات للترتيب
        services = services.annotate(
            price_in_iqd=models.Case(
                models.When(currency='USD', then=models.F('price') * 1500),
                default=models.F('price'),
                output_field=models.DecimalField(max_digits=14, decimal_places=2)
            )
        )

        # ترتيب
        sort = self.request.GET.get('sort', 'newest')
        sort_options = {
            'newest': '-created_at',
            'price_low': 'price_in_iqd',
            'price_high': '-price_in_iqd',
            'rating': '-avg_rating',
        }
        order_by = sort_options.get(sort, '-created_at')
        services = services.order_by(order_by)

        context['services'] = services
        context['services_count'] = services.count()
        context['current_sort'] = sort
        context['subcategories'] = category.subcategories.filter(is_active=True).order_by('order', 'name')

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
