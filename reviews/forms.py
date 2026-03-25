"""
Reviews Forms - نماذج المراجعات
"""

from django import forms
from .models import Review, ReviewImage, ReviewResponse


class ReviewForm(forms.ModelForm):
    """نموذج إضافة مراجعة"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'شاركنا تجربتك مع هذه الخدمة...'
            }),
        }
        labels = {
            'rating': 'التقييم',
            'comment': 'التعليق (اختياري)',
        }


class ReviewImageForm(forms.ModelForm):
    """نموذج رفع صور المراجعة"""
    
    class Meta:
        model = ReviewImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'وصف الصورة (اختياري)'
            }),
        }


class ReviewResponseForm(forms.ModelForm):
    """نموذج رد مقدم الخدمة"""
    
    class Meta:
        model = ReviewResponse
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اكتب ردك على هذه المراجعة...'
            }),
        }
        labels = {
            'response_text': 'الرد',
        }
