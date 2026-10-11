"""
Requests Forms - نماذج طلبات الخدمات
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ServiceRequest


from core.validators import validate_iraqi_phone, normalize_iraqi_phone, IRAQI_PHONE_REGEX


class ServiceRequestForm(forms.ModelForm):
    """نموذج إنشاء طلب خدمة"""
    
    class Meta:
        model = ServiceRequest
        fields = ['customer_notes', 'contact_phone', 'contact_email']
        widgets = {
            'customer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('اكتب أي ملاحظات أو متطلبات خاصة...'),
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '07XXXXXXXXX (مثال: 07701234567)',
                'dir': 'ltr',
                'pattern': IRAQI_PHONE_REGEX,
                'title': _('يرجى إدخال رقم هاتف عراقي صحيح يبدأ بـ 07'),
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('البريد الإلكتروني'),
                'dir': 'ltr',
            }),
        }
        labels = {
            'customer_notes': _('ملاحظات إضافية'),
            'contact_phone': _('رقم التواصل'),
            'contact_email': _('البريد الإلكتروني'),
        }
        help_texts = {
            'customer_notes': _('يمكنك إضافة أي تفاصيل أو متطلبات خاصة بطلبك'),
        }

    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            validate_iraqi_phone(phone)
            return normalize_iraqi_phone(phone, output_format='local')
        return phone


class UpdateStatusForm(forms.ModelForm):
    """نموذج تحديث حالة الطلب"""
    
    class Meta:
        model = ServiceRequest
        fields = ['status', 'staff_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'staff_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('ملاحظات داخلية...'),
            }),
        }
        labels = {
            'status': _('الحالة الجديدة'),
            'staff_notes': _('ملاحظات الموظف'),
        }


class RequestCancelForm(forms.ModelForm):
    """
    نموذج احترافي لإلغاء الطلب مع توثيق الأسباب والملاحظات
    """
    class Meta:
        model = ServiceRequest
        fields = ['cancellation_reason', 'cancellation_notes']
        widgets = {
            'cancellation_reason': forms.RadioSelect(attrs={
                'class': 'form-check-input cancel-reason-radio',
            }),
            'cancellation_notes': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'rows': 3,
                'placeholder': _('يرجى كتابة أية تفاصيل أو ملاحظات إضافية لمساعدتنا على فهم سبب الإلغاء وتحسين الخدمة...'),
            }),
        }
        labels = {
            'cancellation_reason': _('سبب الإلغاء'),
            'cancellation_notes': _('ملاحظات وتوضيحات إضافية'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cancellation_reason'].required = True
        self.fields['cancellation_reason'].empty_label = None

    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get('cancellation_reason')
        notes = cleaned_data.get('cancellation_notes')

        if not reason:
            self.add_error('cancellation_reason', _('يرجى تحديد سبب الإلغاء من الخيارات المتاحة.'))
            
        if reason == 'other' and not (notes and notes.strip()):
            self.add_error('cancellation_notes', _('عند اختيار "سبب آخر"، يرجى كتابة توضيح لسبب الإلغاء في حقل الملاحظات أدناه.'))

        return cleaned_data

