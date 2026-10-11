"""
Core URLs - روابط الصفحات الأساسية
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    path('banner/<int:banner_id>/click/', views.track_banner_click, name='banner_click'),
    path('ajax/apply-coupon/', views.apply_coupon_ajax, name='apply_coupon'),
    path('ajax/captcha/refresh/', views.refresh_captcha_ajax, name='refresh_captcha'),
    # Currency Switcher
    path('currency/switch/<str:currency_code>/', views.switch_currency_view, name='switch_currency'),
    # Error Pages Preview & Offline Shell
    path('offline/', views.offline_view, name='offline'),
    path('errors/404/', views.error_404_view, name='preview_404'),
    path('errors/500/', views.error_500_view, name='preview_500'),
    path('errors/403/', views.error_403_view, name='preview_403'),
    path('errors/400/', views.error_400_view, name='preview_400'),
]
