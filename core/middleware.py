"""
Core Middlewares - برمجيات الوسيط للنظام
"""
from django.conf import settings
from core.views import error_404_view, error_500_view


class DevelopmentErrorPageMiddleware:
    """
    يعرض صفحات الخطأ المخصصة (404 و 500) الجميلة بدلاً من الشاشة الصفراء الفنية لدجانغو
    حتى في وضع التطوير (DEBUG = True)، لضمان تجربة مستخدم وتصميم متكامل.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # إذا كانت الاستجابة 404 لصفحة HTML عادية
        if response.status_code == 404:
            # عدم التدخل في لوحة الأدمن أو الملفات الثابتة والوسائط
            if not request.path.startswith('/admin/') and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
                accept = request.META.get('HTTP_ACCEPT', '')
                if 'text/html' in accept or not accept:
                    return error_404_view(request, exception=None)
                    
        return response


class AdminArabicLocaleMiddleware:
    """
    تفعيل اللغة العربية واتجاه RTL تلقائياً وبشكل كامل للوحة الإدارة (Admin)
    بغض النظر عن لغة متصفح العميل، لضمان تجربة إدارة عربية متكاملة من اليمين إلى اليسار.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.utils import translation
        if request.path.startswith('/admin/'):
            translation.activate('ar')
            request.LANGUAGE_CODE = 'ar'
        response = self.get_response(request)
        return response
