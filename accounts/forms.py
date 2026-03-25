"""
Accounts Forms - نماذج الحسابات
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Provider, UserProfile
import re

class UserRegistrationForm(UserCreationForm):
    """نموذج تسجيل مستخدم جديد (أساسي)"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        label=_('البريد الإلكتروني')
    )
    
    first_name = forms.CharField(max_length=30, required=True, label=_('الاسم الأول'))
    last_name = forms.CharField(max_length=30, required=True, label=_('اسم العائلة'))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['username'].widget.attrs.update({'placeholder': _('اسم المستخدم'), 'dir': 'ltr'})
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'placeholder': _('كلمة المرور')})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'placeholder': _('تأكيد كلمة المرور')})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.replace(' ', '')
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise forms.ValidationError(_('اسم المستخدم يجب أن يحتوي على حروف إنجليزية وأرقام فقط.'))
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError(_('عذراً، اسم المستخدم هذا محجوز مسبقاً.'))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('هذا البريد الإلكتروني مستخدم بالفعل.'))
        return email


class UserRegistrationFormExtended(UserCreationForm):
    """نموذج تسجيل موسع مع معلومات إضافية"""
    
    user_type = forms.ChoiceField(
        choices=[
            ('customer', _('عميل - أريد طلب خدمات')),
            ('provider', _('مقدم خدمة - أريد تقديم خدمات')),
        ],
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'user-type-radio'}),
        label=_('نوع الحساب'),
        initial='customer'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        label=_('البريد الإلكتروني')
    )
    
    first_name = forms.CharField(max_length=30, required=True, label=_('الاسم الأول'))
    last_name = forms.CharField(max_length=30, required=True, label=_('اسم العائلة'))
    
    phone = forms.CharField(max_length=20, required=True, label=_('رقم الهاتف'))
    alternate_phone = forms.CharField(max_length=20, required=False, label=_('رقم هاتف بديل'))
    
    city = forms.CharField(max_length=100, required=True, label=_('المدينة'))
    district = forms.CharField(max_length=100, required=True, label=_('الحي / المنطقة'))
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 3}), label=_('العنوان التفصيلي'))
    postal_code = forms.CharField(max_length=10, required=False, label=_('الرمز البريدي'))
    
    id_type = forms.ChoiceField(choices=UserProfile.IDType.choices, required=True, label=_('نوع الوثيقة'))
    id_number = forms.CharField(max_length=20, required=True, label=_('رقم الوثيقة'))
    id_document = forms.ImageField(required=True, label=_('صورة الوثيقة'))
    
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label=_('تاريخ الميلاد'))
    gender = forms.ChoiceField(choices=[('', _('-- اختر --'))] + list(UserProfile.Gender.choices), required=False, label=_('الجنس'))

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'user_type':
                existing_class = field.widget.attrs.get('class', '')
                if 'form-control' not in existing_class and 'form-select' not in existing_class:
                    if isinstance(field.widget, (forms.Select, forms.RadioSelect)):
                        field.widget.attrs.update({'class': 'form-select ' + existing_class})
                    else:
                        field.widget.attrs.update({'class': 'form-control ' + existing_class})
        
        self.fields['username'].widget.attrs.update({'placeholder': _('اسم المستخدم'), 'dir': 'ltr'})
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'placeholder': _('كلمة المرور')})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'placeholder': _('تأكيد كلمة المرور')})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.replace(' ', '')
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise forms.ValidationError(_('اسم المستخدم يجب أن يحتوي على حروف إنجليزية وأرقام فقط.'))
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError(_('عذراً، اسم المستخدم هذا محجوز مسبقاً.'))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('هذا البريد الإلكتروني مستخدم بالفعل.'))
        return email

    def clean_user_type(self):
        user_type = self.cleaned_data.get('user_type')
        if not user_type:
            return 'customer' # القيمة الافتراضية
        return user_type

    def save(self, commit=True):
        # حفظ المستخدم الأساسي وتشفير كلمة المرور
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        
        if commit:
            user.save()
            
            # جلب الملف الشخصي الذي أنشأته الـ Signal
            # نستخدم get_or_create للأمان
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # تحديث بيانات الملف الشخصي
            user_type = self.cleaned_data.get('user_type', 'customer')
            profile.user_type = user_type
            profile.phone_number = self.cleaned_data.get('phone', '')
            profile.alternate_phone = self.cleaned_data.get('alternate_phone', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.city = self.cleaned_data.get('city', '')
            profile.district = self.cleaned_data.get('district', '')
            profile.postal_code = self.cleaned_data.get('postal_code', '')
            profile.id_type = self.cleaned_data.get('id_type', '')
            profile.id_number = self.cleaned_data.get('id_number', '')
            
            # التعامل مع الملف المرفوع
            id_doc = self.cleaned_data.get('id_document')
            if id_doc:
                profile.id_document = id_doc
                
            profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            profile.gender = self.cleaned_data.get('gender', '')
            profile.save()

            # تعيين المجموعات
            from django.contrib.auth.models import Group
            group_name = 'Customers' if user_type == 'customer' else 'Providers'
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            # إنشاء حساب مقدم الخدمة إذا لزم الأمر
            if user_type == 'provider':
                from services.models import Provider
                Provider.objects.get_or_create(
                    user=user, 
                    defaults={
                        'display_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                        'bio': 'مقدم خدمة جديد'
                    }
                )
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}))
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'date_of_birth', 'gender', 'phone_number', 'alternate_phone', 'address', 'city', 'district', 'postal_code']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email


class DocumentUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['id_type', 'id_number', 'id_document']
        widgets = {
            'id_type': forms.Select(attrs={'class': 'form-select'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'id_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
