"""
Accounts Views - عروض الحسابات
"""

from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserRegistrationFormExtended, UserProfileUpdateForm, DocumentUpdateForm


class CustomLoginView(LoginView):
    """تسجيل الدخول"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirect to appropriate dashboard
        return reverse_lazy('dashboard:redirect')



class CustomLogoutView(LoginRequiredMixin, TemplateView):
    """تسجيل الخروج"""
    template_name = 'registration/logged_out.html'
    
    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        return redirect('core:home')


class RegisterView(CreateView):
    """صفحة التسجيل"""
    template_name = 'accounts/register.html'
    form_class = UserRegistrationFormExtended
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        self.object = form.save()
        messages.success(
            self.request,
            f'تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.'
        )
        return redirect(self.get_success_url())


class ProfileView(LoginRequiredMixin, TemplateView):
    """عرض الملف الشخصي"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # إنشاء profile إذا لم يكن موجوداً
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
        
        profile = user.profile
        context['user_profile'] = profile
        context['completion_percentage'] = profile.calculate_completion()
        context['verification_status'] = profile.get_verification_status()
        
        # إحصائيات
        context['unread_notifications'] = user.notifications.filter(is_read=False).count() if hasattr(user, 'notifications') else 0
        context['recent_requests'] = user.service_requests.all()[:5]
        
        # معلومات المزود
        if profile.is_provider() and hasattr(user, 'provider_profile'):
            context['provider'] = user.provider_profile
            
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """تحديث الملف الشخصي"""
    model = User
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    fields = []  # We'll handle fields manually
    
    def get_object(self):
        return self.request.user
    
    def post(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile
        
        # Update User fields
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update Profile fields
        profile.phone_number = request.POST.get('phone_number', '')
        profile.alternate_phone = request.POST.get('alternate_phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.district = request.POST.get('district', '')
        profile.gender = request.POST.get('gender', '')
        
        # Date of birth
        dob = request.POST.get('date_of_birth')
        if dob:
            from datetime import datetime
            try:
                profile.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
            except:
                pass
        
        # Profile picture
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        # Update Provider info if user is a provider
        if profile.is_provider() and hasattr(user, 'provider_profile'):
            provider = user.provider_profile
            provider.bio = request.POST.get('bio', provider.bio)
            provider.phone = request.POST.get('phone', provider.phone)
            provider.display_name = f"{user.first_name} {user.last_name}".strip() or user.username
            provider.save()
        
        messages.success(request, 'تم تحديث ملفك الشخصي بنجاح!')
        return redirect(self.success_url)


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    """تحديث وثيقة الهوية"""
    model = UserProfile
    form_class = DocumentUpdateForm
    template_name = 'accounts/document_update.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user.profile
    
    def form_valid(self, form):
        # إعادة تعيين حالة التحقق
        form.instance.id_verified = False
        form.instance.verified_at = None
        form.instance.verified_by = None
        messages.info(
            self.request, 
            'تم تحديث الوثيقة. سيتم مراجعتها من قبل الإدارة.'
        )
        return super().form_valid(form)


class ProviderAgreementView(LoginRequiredMixin, TemplateView):
    """صفحة تعهد مقدم الخدمة"""
    template_name = 'accounts/provider_agreement.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import datetime
        context['current_date'] = datetime.now()
        # يمكن إضافة نسب العمولة الافتراضية
        context['commission_percentage'] = 10
        context['commission_fixed'] = 0
        return context
