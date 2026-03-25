"""
Core Context Processors - معالجات السياق
"""

from django.conf import settings


def site_settings(request):
    """إضافة إعدادات الموقع للسياق"""
    return {
        'SITE_NAME': 'نظام الخدمات',
        'SITE_DESCRIPTION': 'منصة متكاملة لعرض وطلب الخدمات',
        'DEBUG': settings.DEBUG,
    }
