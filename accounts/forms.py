"""
Accounts Forms - نماذج الحسابات
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Provider, UserProfile
import os


class UserRegistrationForm(UserCreationForm):
    """نموذج تسجيل مستخدم جديد"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('البريد الإلكتروني'),
            'dir': 'ltr',
        }),
        label=_('البريد الإلكتروني')
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('الاسم الأول'),
        }),
        label=_('الاسم الأول')
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('اسم العائلة'),
        }),
        label=_('اسم العائلة')
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم المستخدم'),
                'dir': 'ltr',
            }),
        }
        labels = {
            'username': _('اسم المستخدم'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('كلمة المرور'),
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('تأكيد كلمة المرور'),
        })
        self.fields['password1'].label = _('كلمة المرور')
        self.fields['password2'].label = _('تأكيد كلمة المرور')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('هذا البريد الإلكتروني مستخدم بالفعل.'))
        return email


class UserRegistrationFormExtended(UserCreationForm):
    """نموذج تسجيل موسع مع معلومات إضافية
    Extended registration form with additional profile information
    """
    
    # User fields
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('البريد الإلكتروني'),
            'dir': 'ltr',
        }),
        label=_('البريد الإلكتروني')
    )
    
    # User Type Selection
    user_type = forms.ChoiceField(
        choices=[
            ('customer', _('عميل - أريد طلب خدمات')),
            ('provider', _('مقدم خدمة - أريد تقديم خدمات')),
        ],
        widget=forms.RadioSelect(attrs={'class': 'user-type-radio'}),
        label=_('نوع الحساب'),
        initial='customer'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('الاسم الأول'),
        }),
        label=_('الاسم الأول')
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('اسم العائلة'),
        }),
        label=_('اسم العائلة')
    )
    
    # Phone (required - no format validation)
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('رقم الهاتف'),
            'dir': 'ltr',
        }),
        label=_('رقم الهاتف'),
        help_text=_('أي رقم هاتف')
    )
    
    # Alternate phone (optional)
    alternate_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('رقم هاتف بديل'),
            'dir': 'ltr',
        }),
        label=_('رقم هاتف بديل'),
        help_text=_('اختياري')
    )
    
    
    # Address fields
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('مثال: العراق، بغداد'),
        }),
        label=_('المدينة')
    )
    
    district = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('مثال: بغداد'),
        }),
        label=_('الحي / المنطقة')
    )
    
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('العنوان التفصيلي - الشارع، رقم المبنى، إلخ'),
        }),
        label=_('العنوان التفصيلي')
    )
    
    postal_code = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('مثال: 12345'),
            'dir': 'ltr',
        }),
        label=_('الرمز البريدي'),
        help_text=_('اختياري')
    )
    
    # ID Verification fields
    id_type = forms.ChoiceField(
        choices=UserProfile.IDType.choices,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label=_('نوع الوثيقة')
    )
    
    id_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('رقم الهوية/الجواز/الإقامة'),
            'dir': 'ltr',
        }),
        label=_('رقم الوثيقة')
    )
    
    id_document = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png,image/jpg,application/pdf',
        }),
        label=_('صورة الوثيقة'),
        help_text=_('يرجى رفع صورة واضحة للهوية/الجواز/الإقامة (JPG, PNG, PDF - حد أقصى 5MB)')
    )
    
    # Optional fields
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label=_('تاريخ الميلاد'),
        help_text=_('اختياري')
    )
    
    gender = forms.ChoiceField(
        choices=[('', _('-- اختر --'))] + list(UserProfile.Gender.choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label=_('الجنس'),
        help_text=_('اختياري')
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('اسم المستخدم'),
                'dir': 'ltr',
            }),
        }
        labels = {
            'username': _('اسم المستخدم'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('كلمة المرور'),
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('تأكيد كلمة المرور'),
        })
        self.fields['password1'].label = _('كلمة المرور')
        self.fields['password2'].label = _('تأكيد كلمة المرور')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('هذا البريد الإلكتروني مستخدم بالفعل.'))
        return email
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # التحقق من صيغة الهاتف السعودي
        if phone:
            # إزالة المسافات والفواصل
            phone = phone.replace(' ', '').replace('-', '')
            # التحقق من أنه يبدأ بـ +966 أو 966 أو 05
            if not (phone.startswith('+966') or phone.startswith('966') or phone.startswith('05')):
                raise ValidationError(_('رقم الهاتف يجب أن يبدأ بـ +966 أو 05'))
        return phone
    
    def clean_id_document(self):
        document = self.cleaned_data.get('id_document')
        if document:
            # التحقق من حجم الملف (5MB)
            if document.size > 5 * 1024 * 1024:
                raise ValidationError(_('حجم الملف يجب أن يكون أقل من 5 ميجابايت'))
            
            # التحقق من نوع الملف
            ext = os.path.splitext(document.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
            if ext not in valid_extensions:
                raise ValidationError(_('نوع الملف غير مدعوم. يرجى رفع ملف JPG أو PNG أو PDF'))
        return document
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # تحديث أو إنشاء UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.alternate_phone = self.cleaned_data.get('alternate_phone', '')
            profile.city = self.cleaned_data.get('city', '')
            profile.district = self.cleaned_data.get('district', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.postal_code = self.cleaned_data.get('postal_code', '')
            profile.id_type = self.cleaned_data.get('id_type', '')
            profile.id_number = self.cleaned_data.get('id_number', '')
            profile.id_document = self.cleaned_data.get('id_document')
            profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            profile.gender = self.cleaned_data.get('gender', '')
            profile.save()
        
        return user


class UserUpdateForm(forms.ModelForm):
    """نموذج تحديث بيانات المستخدم"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'dir': 'ltr',
            }),
        }
        labels = {
            'first_name': _('الاسم الأول'),
            'last_name': _('اسم العائلة'),
            'email': _('البريد الإلكتروني'),
        }


class ProviderUpdateForm(forms.ModelForm):
    """نموذج تحديث بيانات مقدم الخدمة"""
    
    class Meta:
        model = Provider
        fields = ['display_name', 'bio', 'phone', 'avatar']
        widgets = {
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'dir': 'ltr',
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'display_name': _('الاسم المعروض'),
            'bio': _('نبذة تعريفية'),
            'phone': _('رقم الهاتف'),
            'avatar': _('الصورة الشخصية'),
        }


class UserProfileUpdateForm(forms.ModelForm):
    """نموذج تحديث الملف الشخصي الموسع"""
    
    # User fields (read-only display)
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }),
        label=_('الاسم الأول')
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        }),
        label=_('اسم العائلة')
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'dir': 'ltr',
        }),
        label=_('البريد الإلكتروني')
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'date_of_birth', 'gender',
            'phone_number', 'alternate_phone',
            'address', 'city', 'district', 'postal_code',
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/jpg',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'dir': 'ltr',
            }),
            'alternate_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'dir': 'ltr',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'dir': 'ltr',
            }),
        }
        labels = {
            'profile_picture': _('الصورة الشخصية'),
            'date_of_birth': _('تاريخ الميلاد'),
            'gender': _('الجنس'),
            'phone_number': _('رقم الهاتف'),
            'alternate_phone': _('رقم هاتف بديل'),
            'address': _('العنوان التفصيلي'),
            'city': _('المدينة'),
            'district': _('الحي/المنطقة'),
            'postal_code': _('الرمز البريدي'),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if hasattr(picture, 'size') and picture.size > 5 * 1024 * 1024:
                raise ValidationError(_('حجم الصورة يجب أن يكون أقل من 5 ميجابايت'))
        return picture


class DocumentUpdateForm(forms.ModelForm):
    """نموذج تحديث وثيقة الهوية"""
    
    class Meta:
        model = UserProfile
        fields = ['id_type', 'id_number', 'id_document']
        widgets = {
            'id_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'dir': 'ltr',
            }),
            'id_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/jpg,application/pdf',
            }),
        }
        labels = {
            'id_type': _('نوع الوثيقة'),
            'id_number': _('رقم الوثيقة'),
            'id_document': _('صورة الوثيقة'),
        }
    
    def clean_id_document(self):
        document = self.cleaned_data.get('id_document')
        if document and hasattr(document, 'size'):
            if document.size > 5 * 1024 * 1024:
                raise ValidationError(_('حجم الملف يجب أن يكون أقل من 5 ميجابايت'))
            
            ext = os.path.splitext(document.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
            if ext not in valid_extensions:
                raise ValidationError(_('نوع الملف غير مدعوم. يرجى رفع ملف JPG أو PNG أو PDF'))
        return document
