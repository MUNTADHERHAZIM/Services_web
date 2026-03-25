"""
Requests Forms - نماذج طلبات الخدمات
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ServiceRequest


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
                'placeholder': _('رقم الهاتف للتواصل'),
                'dir': 'ltr',
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
