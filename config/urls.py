"""
URL Configuration for Service Catalog System
نظام عرض الخدمات - روابط المشروع الرئيسية
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# تخصيص لوحة الإدارة المركزية
admin.site.site_header = 'منصة خدماتي | لوحة الإدارة والتحكم'
admin.site.site_title = 'إدارة منصة خدماتي'
admin.site.index_title = 'لوحة التحكم المركزية بالنظام'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('services/', include('services.urls', namespace='services')),
    path('requests/', include('requests.urls', namespace='requests')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('favorites/', include('favorites.urls', namespace='favorites')),
    path('wallet/', include('wallet.urls', namespace='wallet')),
    path('conversations/', include('conversations.urls', namespace='conversations')),
]

from core.views import service_worker_view, manifest_view
urlpatterns += [
    path('sw.js', service_worker_view, name='service_worker'),
    path('manifest.json', manifest_view, name='pwa_manifest'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# صفحات الخطأ المخصصة - Custom Error Handlers
handler404 = 'core.views.error_404_view'
handler500 = 'core.views.error_500_view'
handler403 = 'core.views.error_403_view'
handler400 = 'core.views.error_400_view'

