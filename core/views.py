"""
Core Views - العروض الأساسية
"""

from django.views.generic import TemplateView
from django.db import models
from django.db.models import Count, Avg
from services.models import Category, Service
from accounts.models import Provider


class HomeView(TemplateView):
    """الصفحة الرئيسية"""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # الخدمات المميزة
        context['featured_services'] = Service.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related('category', 'provider__user').prefetch_related('tags')[:6]
        
        # أحدث الخدمات
        context['latest_services'] = Service.objects.filter(
            is_active=True
        ).select_related('category', 'provider__user')[:6]
        
        # أفضل مقدمي الخدمات
        context['top_providers'] = Provider.objects.filter(
            is_active=True
        ).select_related('user').order_by('-is_verified', '-completed_orders')[:4]
        
        # التصنيفات النشطة
        context['categories'] = Category.objects.filter(
            is_active=True
        ).annotate(
            services_count=Count('services', filter=models.Q(services__is_active=True))
        ).order_by('order', 'name')[:8]
        
        # إحصائيات
        context['stats'] = {
            'services_count': Service.objects.filter(is_active=True).count(),
            'categories_count': Category.objects.filter(is_active=True).count(),
            'providers_count': Provider.objects.filter(is_active=True).count(),
            'clients_count': 1000,  # يمكن حسابها من عدد المستخدمين النشطين
        }
        
        return context


class AboutView(TemplateView):
    """صفحة من نحن"""
    template_name = 'core/about.html'


class ContactView(TemplateView):
    """صفحة اتصل بنا"""
    template_name = 'core/contact.html'


class TermsOfServiceView(TemplateView):
    """صفحة شروط الاستخدام"""
    template_name = 'core/terms_of_service.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import datetime
        context['current_date'] = datetime.now()
        return context

