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
        
        # التصنيفات الرئيسية النشطة مع تصنيفاتها الفرعية
        context['categories'] = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).prefetch_related('subcategories').order_by('order', 'name')[:12]
        
        # إحصائيات
        context['stats'] = {
            'services_count': Service.objects.filter(is_active=True).count(),
            'categories_count': Category.objects.filter(is_active=True, parent__isnull=True).count(),
            'providers_count': Provider.objects.filter(is_active=True).count(),
            'clients_count': 1000,
        }

        # العروض والبنرات الترويجية
        from core.models import PromotionalBanner
        from django.utils import timezone
        now = timezone.now()

        # بنرات السلايدر الرئيسي
        context['hero_banners'] = PromotionalBanner.objects.filter(
            banner_type=PromotionalBanner.BannerType.HERO_SLIDER,
            is_active=True
        ).filter(
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=now)
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        ).order_by('order', '-created_at')[:4]

        # بطاقات العروض والصفقات الترويجية
        context['promo_cards'] = PromotionalBanner.objects.filter(
            banner_type=PromotionalBanner.BannerType.PROMO_CARD,
            is_active=True
        ).order_by('order', '-created_at')[:3]

        # صفقات اليوم والخصومات السارية (Flash Deals)
        context['flash_deals'] = Service.objects.filter(
            is_active=True,
            original_price__isnull=False,
            price__isnull=False,
            original_price__gt=models.F('price')
        ).select_related('category', 'provider__user').prefetch_related('tags')[:6]

        return context


def track_banner_click(request, banner_id):
    """تتبع وتسجيل نقرات البنرات الترويجية ثم التوجيه للرابط"""
    from django.shortcuts import get_object_or_404, redirect
    from core.models import PromotionalBanner

    banner = get_object_or_404(PromotionalBanner, id=banner_id)
    banner.increment_clicks()
    return redirect(banner.cta_url or '/')


def apply_coupon_ajax(request):
    """التحقق من كوبون الخصم وتطبيقه عبر AJAX"""
    from django.http import JsonResponse
    from core.models import Coupon
    from services.models import Service
    from decimal import Decimal

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'طريقة الطلب غير صالحة.'}, status=405)

    code = request.POST.get('code', '').strip().upper()
    service_id = request.POST.get('service_id')

    if not code:
        return JsonResponse({'success': False, 'message': 'يرجى إدخال رمز الكوبون.'})

    try:
        service = Service.objects.get(id=service_id, is_active=True)
    except Service.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'الخدمة غير موجودة.'})

    coupon = Coupon.objects.filter(code__iexact=code).first()
    if not coupon:
        return JsonResponse({'success': False, 'message': 'كوبون الخصم المدخل غير صحيح.'})

    base_price = service.price or Decimal('0')
    is_valid, msg = coupon.is_valid_for(base_price)
    if not is_valid:
        return JsonResponse({'success': False, 'message': msg})

    discount = coupon.calculate_discount(base_price)
    final_price = max(Decimal('0'), base_price - discount)

    currency = getattr(service, 'currency', 'IQD')
    if currency == 'USD':
        discount_msg = f'تم تفعيل الخصم بنجاح! وفرت ${discount}'
    else:
        discount_msg = f'تم تفعيل الخصم بنجاح! وفرت {int(discount):,} د.ع'

    return JsonResponse({
        'success': True,
        'coupon_id': coupon.id,
        'coupon_code': coupon.code,
        'currency': currency,
        'discount_amount': float(discount),
        'final_price': float(final_price),
        'original_price': float(base_price),
        'message': discount_msg
    })


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


def error_404_view(request, exception=None):
    """عرض صفحة الخطأ 404 المخصصة"""
    from django.shortcuts import render
    return render(request, '404.html', status=404)


def error_500_view(request):
    """عرض صفحة الخطأ 500 المخصصة"""
    from django.shortcuts import render
    return render(request, '500.html', status=500)


def error_403_view(request, exception=None):
    """عرض صفحة الخطأ 403 المخصصة"""
    from django.shortcuts import render
    return render(request, '403.html', status=403)


def error_400_view(request, exception=None):
    """عرض صفحة الخطأ 400 المخصصة"""
    from django.shortcuts import render
    return render(request, '400.html', status=400)


def service_worker_view(request):
    """تخديم ملف عامل الخدمة Service Worker من جذر الموقع مع رأس الصلاحيات الكاملة"""
    import os
    from django.conf import settings
    from django.http import HttpResponse

    sw_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    try:
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        content = "console.log('SW file not found');"

    response = HttpResponse(content, content_type='application/javascript; charset=utf-8')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def manifest_view(request):
    """تخديم ملف مانيفست التطبيق Web App Manifest من جذر الموقع"""
    import os
    from django.conf import settings
    from django.http import HttpResponse

    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        content = "{}"

    response = HttpResponse(content, content_type='application/manifest+json; charset=utf-8')
    response['Cache-Control'] = 'public, max-age=86400'
    return response


def offline_view(request):
    """عرض شاشة العمل بدون اتصال بالإنترنت (Offline Mode)"""
    from django.shortcuts import render
    return render(request, 'offline.html')


def switch_currency_view(request, currency_code):
    """تبديل العملة المفضلة للمستخدم (IQD دينار عراقي أو USD دولار) وتخزينها في الجلسة"""
    from django.http import JsonResponse, HttpResponseRedirect
    code = currency_code.upper()
    if code in ['IQD', 'USD']:
        request.session['user_currency'] = code
    redirect_url = request.META.get('HTTP_REFERER', '/')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'currency': code})
    return HttpResponseRedirect(redirect_url)


def refresh_captcha_ajax(request):
    """توليد كود كابتشا جديد وتوقيعه رقمياً عبر AJAX"""
    from core.captcha import generate_captcha_challenge
    from django.http import JsonResponse

    challenge = generate_captcha_challenge()
    return JsonResponse({
        'success': True,
        'token': challenge['token'],
        'svg': challenge['svg'],
    })




