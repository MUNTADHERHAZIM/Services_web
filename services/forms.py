"""
Services Forms - نماذج الخدمات
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Category, Service, Tag


class ServiceForm(forms.ModelForm):
    """نموذج إنشاء وتعديل الخدمة"""
    
    class Meta:
        model = Service
        fields = [
            'category', 'title', 'summary', 'description', 
            'level', 'price', 'price_note', 'duration', 
            'cover_image', 'video_intro', 'tags', 'is_active'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('عنوان الخدمة')}),
            'summary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('ملخص قصير للخدمة')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('وصف تفصيلي للخدمة')}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('السعر')}),
            'price_note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('مثال: يبدأ من')}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('مثال: 3-5 أيام')}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'video_intro': forms.URLInput(attrs={'class': 'form-control', 'placeholder': _('رابط فيديو تعريفي')}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select select2'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ServiceSearchForm(forms.Form):
    """نموذج البحث والفلترة"""
    
    SORT_CHOICES = [
        ('newest', _('الأحدث')),
        ('oldest', _('الأقدم')),
        ('price_low', _('الأقل سعراً')),
        ('price_high', _('الأعلى سعراً')),
        ('rating', _('الأعلى تقييماً')),
        ('popular', _('الأكثر مشاهدة')),
    ]
    
    RATING_CHOICES = [
        ('', _('جميع التقييمات')),
        ('4', _('4 نجوم فأكثر')),
        ('3', _('3 نجوم فأكثر')),
        ('2', _('2 نجوم فأكثر')),
    ]

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('ابحث عن خدمة...'),
            'autocomplete': 'off',
        }),
        label=_('البحث')
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label=_('جميع التصنيفات'),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label=_('التصنيف')
    )
    
    price_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('من'),
        }),
        label=_('السعر (من)')
    )
    
    price_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('إلى'),
        }),
        label=_('السعر (إلى)')
    )
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label=_('التقييم')
    )
    
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='newest',
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label=_('الترتيب')
    )
