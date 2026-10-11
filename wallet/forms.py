"""
Wallet Forms - نماذج إدخال طلبات شحن وسحب الرصيد المالية
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from core.validators import validate_iraqi_phone
from .models import DepositRequest, WithdrawalRequest, DepositMethod


class DepositRequestForm(forms.ModelForm):
    """
    نموذج تقديم طلب شحن الرصيد بإشعار التحويل البنكي أو المحفظة الإلكترونية
    """
    class Meta:
        model = DepositRequest
        fields = [
            'deposit_method',
            'amount',
            'sender_name',
            'sender_phone',
            'transaction_reference',
            'receipt_image',
        ]
        widgets = {
            'deposit_method': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_deposit_method'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg fw-bold',
                'placeholder': '50',
                'min': '1',
                'step': 'any',
                'id': 'id_deposit_amount'
            }),
            'sender_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم صاحب الحساب أو المحفظة المحوِّل منه بالكامل'
            }),
            'sender_phone': forms.TextInput(attrs={
                'class': 'form-control text-start font-monospace',
                'placeholder': '07XXXXXXXXX',
                'dir': 'ltr'
            }),
            'transaction_reference': forms.TextInput(attrs={
                'class': 'form-control font-monospace text-uppercase',
                'placeholder': 'مثال: رقم الحوالة، رمز المعاملة، أو الرقم المرجعي'
            }),
            'receipt_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'receipt_file_input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deposit_method'].queryset = DepositMethod.objects.filter(is_active=True).order_by('display_order', 'id')
        self.fields['deposit_method'].empty_label = "-- اختر وسيلة التحويل والشحن --"

    def clean_sender_phone(self):
        phone = self.cleaned_data.get('sender_phone', '')
        if phone:
            # التحقق والتنظيف والتأكد من صيغة الهاتف العراقي
            try:
                phone = validate_iraqi_phone(phone)
            except forms.ValidationError:
                # إذا كانت حوالة دولية أو وسيلة تقبل أرقاماً غير محلية، نسمح بتجاوز التحقق الصارم إذا لم يكن رقماً عراقياً
                pass
        return phone

    def clean_receipt_image(self):
        image = self.cleaned_data.get('receipt_image')
        if not image:
            raise forms.ValidationError(_("يرجى إرفاق صورة واضحة لوصل أو إشعار التحويل المالي."))

        # التحقق من حجم الملف (الحد الأقصى 10 ميغابايت)
        max_size = 10 * 1024 * 1024
        if image.size > max_size:
            raise forms.ValidationError(_("حجم الصورة كبير جداً! الحد الأقصى المسموح به هو 10 ميغابايت."))

        # التحقق من نوع الملف
        content_type = getattr(image, 'content_type', '')
        if content_type and not content_type.startswith('image/'):
            raise forms.ValidationError(_("الملف المرفق غير صالح. يرجى رفع صورة بصيغة JPG أو PNG أو WEBP."))

        return image

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('deposit_method')
        amount = cleaned_data.get('amount')

        if method and amount:
            if amount < method.min_amount:
                self.add_error('amount', _(f"الحد الأدنى للشحن عبر وسيلة ({method.name}) هو ${method.min_amount}."))
            elif amount > method.max_amount:
                self.add_error('amount', _(f"الحد الأقصى للشحن عبر وسيلة ({method.name}) هو ${method.max_amount}."))

        return cleaned_data


class WithdrawalRequestForm(forms.Form):
    """
    نموذج طلب سحب الأرباح والرصيد المتاح من المحفظة
    """
    method = forms.ChoiceField(
        choices=WithdrawalRequest.WithdrawalMethod.choices,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'withdrawal_method_select'}),
        label=_("طريقة الاستلام والسحب")
    )
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('5.00'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg fw-bold',
            'placeholder': '10',
            'min': '5',
            'step': 'any',
            'id': 'withdrawal_amount_input'
        }),
        label=_("المبلغ المطلوب سحبه ($)")
    )
    account_holder = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الاسم الكامل الثلاثي لصاحب الحساب المستلم'
        }),
        label=_("اسم المستلم الكامل")
    )
    account_number = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control font-monospace',
            'placeholder': 'رقم محفظة زين كاش / رقم بطاقة كي كارد / هاتف المستلم (ويسترن يونيون) / الآيبان IBAN'
        }),
        label=_("رقم الحساب / المحفظة / هاتف المستلم")
    )
    bank_or_branch = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم المصرف والفرع، أو الدولة والمدينة لاستلام ويسترن يونيون'
        }),
        label=_("المصرف / الفرع / مدينة الاستلام (اختياري)")
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'أي تعليمات أو ملاحظات إضافية لتسهيل إرسال الحوالة'
        }),
        required=False,
        label=_("ملاحظات إضافية")
    )

    def __init__(self, wallet=None, *args, **kwargs):
        self.wallet = wallet
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount or amount <= Decimal('0'):
            raise forms.ValidationError(_("يرجى إدخال مبلغ سحب صحيح أكبر من الصفر."))

        if self.wallet and amount > self.wallet.available_balance:
            raise forms.ValidationError(
                _(f"عذراً، المبلغ المطلوب (${amount}) يتجاوز رصيدك المتاح الحالي (${self.wallet.available_balance}).")
            )

        return amount

    def get_account_info_dict(self):
        """تحويل حقول الإدخال إلى كائن بيانات حساب مهيكل بصيغة JSON"""
        data = self.cleaned_data
        return {
            'account_holder': data.get('account_holder', '').strip(),
            'account_number': data.get('account_number', '').strip(),
            'bank_or_branch': data.get('bank_or_branch', '').strip(),
            'notes': data.get('notes', '').strip(),
        }
