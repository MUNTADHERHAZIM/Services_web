"""
Accounts URLs - روابط الحسابات
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import ajax_views

app_name = 'accounts'

urlpatterns = [
    # AJAX endpoints
    path('ajax/check-username/', ajax_views.check_username, name='check_username'),
    path('ajax/check-email/', ajax_views.check_email, name='check_email'),
    
    # تسجيل الدخول والخروج
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # التسجيل
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # الملف الشخصي
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/document/update/', views.DocumentUpdateView.as_view(), name='document_update'),
    
    # إعادة تعيين كلمة المرور
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    # Provider Agreement
    path('provider-agreement/', views.ProviderAgreementView.as_view(), name='provider_agreement'),
]
