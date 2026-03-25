"""
Requests URLs - روابط طلبات الخدمات
"""

from django.urls import path
from . import views

app_name = 'requests'

urlpatterns = [
    # إنشاء طلب جديد
    path('create/<slug:service_slug>/', views.ServiceRequestCreateView.as_view(), name='request_create'),
    
    # قائمة طلباتي
    path('my-requests/', views.MyRequestsListView.as_view(), name='my_requests'),
    
    # تفاصيل طلب
    path('<int:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    
    # تحديث حالة الطلب
    path('<int:pk>/update-status/', views.UpdateRequestStatusView.as_view(), name='update_status'),
    
    # إلغاء طلب
    path('<int:pk>/cancel/', views.CancelRequestView.as_view(), name='cancel_request'),
    
    # الإشعارات
    path('notifications/', views.NotificationsListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_read'),
]
