"""
Services URLs - روابط الخدمات
"""

from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # قائمة الخدمات
    path('', views.ServiceListView.as_view(), name='service_list'),
    
    # إدارة الخدمات (للمزودين)
    path('create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('service/<slug:slug>/update/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('service/<slug:slug>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    
    # تفاصيل خدمة
    path('service/<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
    
    # تصنيف معين
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # مقدم خدمة معين
    path('provider/<slug:username>/', views.ProviderDetailView.as_view(), name='provider_detail'),
    
    # خدمات وسم معين
    path('tag/<slug:slug>/', views.TagServicesView.as_view(), name='tag_services'),
]
