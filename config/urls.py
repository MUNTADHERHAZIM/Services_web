"""
URL Configuration for Service Catalog System
نظام عرض الخدمات - روابط المشروع الرئيسية
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# تخصيص لوحة الإدارة
admin.site.site_header = 'نظام إدارة الخدمات'
admin.site.site_title = 'لوحة التحكم'
admin.site.index_title = 'مرحباً بك في لوحة إدارة الخدمات'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('services/', include('services.urls', namespace='services')),
    path('requests/', include('requests.urls', namespace='requests')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
