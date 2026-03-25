"""
Dashboard URLs - روابط لوحة التحكم
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard Routing
    path('', views.DashboardRedirectView.as_view(), name='redirect'),
    path('customer/', views.CustomerDashboardView.as_view(), name='customer'),
    path('provider/', views.ProviderDashboardView.as_view(), name='provider'),
    path('provider/services/', views.ProviderServiceListView.as_view(), name='provider_services'),
    path('provider/requests/', views.ProviderRequestListView.as_view(), name='provider_requests'),
    path('admin/', views.DashboardHomeView.as_view(), name='admin'),
    
    # Admin - الصفحة الرئيسية
    path('admin/home/', views.DashboardHomeView.as_view(), name='home'),
    
    # إدارة الخدمات
    path('admin/services/', views.ManageServicesView.as_view(), name='manage_services'),
    path('admin/services/<int:pk>/toggle/', views.ToggleServiceActiveView.as_view(), name='toggle_service'),
    
    # إدارة الطلبات
    path('admin/requests/', views.ManageRequestsView.as_view(), name='manage_requests'),
    
    # إدارة التصنيفات
    path('admin/categories/', views.ManageCategoriesView.as_view(), name='manage_categories'),
    
    # إدارة مقدمي الخدمات
    path('admin/providers/', views.ManageProvidersView.as_view(), name='manage_providers'),
    path('admin/providers/<int:pk>/toggle-verify/', views.ToggleProviderVerifiedView.as_view(), name='toggle_provider_verify'),
]
