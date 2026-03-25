"""
Accounts Models - نماذج الحسابات
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator, RegexValidator
from django.utils import timezone
import os


class Provider(models.Model):
    """
    مقدم الخدمة - Professional Service Provider
    """
    class Level(models.TextChoices):
        NEW = 'new', _('مبتدئ')
        LEVEL_ONE = 'level_1', _('المستوى الأول')
        LEVEL_TWO = 'level_2', _('المستوى الثاني')
        LEVEL_THREE = 'level_3', _('المستوى الثالث')
        TOP_RATED = 'top_rated', _('الأعلى تقييماً')
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='provider_profile',
        verbose_name=_('المستخدم')
    )
    display_name = models.CharField(
        max_length=100,
        verbose_name=_('الاسم المعروض')
    )
    title = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('المسمى الوظيفي'),
        help_text=_('مثال: مصمم جرافيك محترف')
    )
    bio = models.TextField(
        blank=True,
        verbose_name=_('نبذة تعريفية')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('رقم الهاتف')
    )
    avatar = models.ImageField(
        upload_to='providers/avatars/',
        blank=True,
        null=True,
        verbose_name=_('الصورة الشخصية')
    )
    cover_image = models.ImageField(
        upload_to='providers/covers/',
        blank=True,
        null=True,
        verbose_name=_('صورة الغلاف')
    )
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.NEW,
        verbose_name=_('المستوى')
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('السعر بالساعة')
    )
    response_time = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('وقت الاستجابة'),
        help_text=_('مثال: خلال ساعة واحدة')
    )
    languages = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('اللغات')
    )
    skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('المهارات')
    )
    website = models.URLField(blank=True, verbose_name=_('الموقع الإلكتروني'))
    linkedin = models.URLField(blank=True, verbose_name=_('لينكد إن'))
    twitter = models.URLField(blank=True, verbose_name=_('تويتر'))
    instagram = models.URLField(blank=True, verbose_name=_('إنستغرام'))
    youtube = models.URLField(blank=True, verbose_name=_('يوتيوب'))
    total_orders = models.PositiveIntegerField(default=0, verbose_name=_('إجمالي الطلبات'))
    completed_orders = models.PositiveIntegerField(default=0, verbose_name=_('الطلبات المكتملة'))
    cancelled_orders = models.PositiveIntegerField(default=0, verbose_name=_('الطلبات الملغاة'))
    is_verified = models.BooleanField(default=False, verbose_name=_('موثق'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))

    class Meta:
        verbose_name = _('مقدم خدمة')
        verbose_name_plural = _('مقدمو الخدمات')
        ordering = ['-created_at']

    def __str__(self):
        return self.display_name

    def get_services_count(self):
        return self.services.filter(is_active=True).count()

    def get_average_rating(self):
        from django.db.models import Avg
        avg = self.services.filter(is_active=True).aggregate(avg_rating=Avg('avg_rating'))['avg_rating']
        return round(avg, 1) if avg else 0

    def get_total_reviews(self):
        from django.db.models import Sum
        total = self.services.filter(is_active=True).aggregate(total=Sum('total_reviews'))['total']
        return total or 0

    def get_completion_rate(self):
        if self.total_orders == 0:
            return 0
        return (self.completed_orders / self.total_orders) * 100

    def get_skills_list(self):
        if isinstance(self.skills, list):
            return self.skills
        return []

    def get_languages_list(self):
        if isinstance(self.languages, list):
            return self.languages
        return []


class UserProfile(models.Model):
    """
    الملف الشخصي الموسع للمستخدم
    Extended User Profile with ID verification and contact information
    """
    
    class IDType(models.TextChoices):
        NATIONAL_ID = 'national_id', _('بطاقة الهوية الوطنية')
        PASSPORT = 'passport', _('جواز السفر')
        RESIDENCE = 'iqama', _('الإقامة')
    
    class Gender(models.TextChoices):
        MALE = 'male', _('ذكر')
        FEMALE = 'female', _('أنثى')
        OTHER = 'other', _('آخر')
    
    class UserType(models.TextChoices):
        CUSTOMER = 'customer', _('عميل')
        PROVIDER = 'provider', _('مقدم خدمة')
        ADMIN = 'admin', _('مدير')
    
    # Relationship to User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('المستخدم')
    )
    
    # User Type & Role
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CUSTOMER,
        verbose_name=_('نوع المستخدم')
    )
    
    # Personal Information
    profile_picture = models.ImageField(
        upload_to='profiles/pictures/',
        blank=True,
        null=True,
        verbose_name=_('الصورة الشخصية')
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الميلاد')
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        verbose_name=_('الجنس')
    )
    
    # Contact Information
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('رقم الهاتف'),
        help_text=_('أدخل رقم هاتفك')
    )
    alternate_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('رقم هاتف بديل')
    )
    
    # Address Information
    address = models.TextField(
        blank=True,
        verbose_name=_('العنوان التفصيلي')
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('المدينة')
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('المنطقة/الحي')
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_('الرمز البريدي')
    )
    
    # ID Verification
    id_type = models.CharField(
        max_length=20,
        choices=IDType.choices,
        blank=True,
        verbose_name=_('نوع الوثيقة')
    )
    id_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('رقم الوثيقة')
    )
    id_document = models.FileField(
        upload_to='documents/ids/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])],
        verbose_name=_('صورة الوثيقة'),
        help_text=_('JPG, PNG, أو PDF - حد أقصى 5MB')
    )
    id_verified = models.BooleanField(
        default=False,
        verbose_name=_('تم التحقق من الهوية')
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ التحقق')
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_profiles',
        verbose_name=_('تم التحقق بواسطة')
    )
    verification_notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات التحقق')
    )
    
    # Provider Approval (for provider user_type only)
    provider_approved = models.BooleanField(
        default=False,
        verbose_name=_('موافقة مزود الخدمة'),
        help_text=_('يجب الموافقة على المزودين قبل السماح لهم بإنشاء خدمات')
    )
    provider_approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ موافقة المزود')
    )
    provider_approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_provider_profiles',
        verbose_name=_('تمت الموافقة بواسطة')
    )
    
    # Profile Completion
    profile_completed = models.BooleanField(
        default=False,
        verbose_name=_('الملف الشخصي مكتمل')
    )
    completion_percentage = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('نسبة الاكتمال')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )
    
    class Meta:
        verbose_name = _('الملف الشخصي')
        verbose_name_plural = _('الملفات الشخصية')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - Profile'
    
    def calculate_completion(self):
        """حساب نسبة اكتمال الملف الشخصي"""
        fields = [
            bool(self.profile_picture),
            bool(self.date_of_birth),
            bool(self.gender),
            bool(self.phone_number),
            bool(self.address),
            bool(self.city),
            bool(self.district),
            bool(self.id_type),
            bool(self.id_number),
            bool(self.id_document),
            bool(self.date_of_birth),
            bool(self.gender),
        ]
        completed = sum(fields)
        total = len(fields)
        percentage = int((completed / total) * 100)
        return percentage
    
    def update_completion(self):
        """تحديث نسبة الاكتمال"""
        self.completion_percentage = self.calculate_completion()
        self.profile_completed = self.completion_percentage >= 80
        self.save(update_fields=['completion_percentage', 'profile_completed'])
    
    def get_masked_id_number(self):
        """إرجاع رقم الهوية مع إخفاء جزء منه للخصوصية"""
        if not self.id_number:
            return ''
        if len(self.id_number) <= 4:
            return '*' * len(self.id_number)
        return self.id_number[:2] + '*' * (len(self.id_number) - 4) + self.id_number[-2:]
    
    def get_verification_status(self):
        """إرجاع حالة التحقق بشكل واضح"""
        if self.id_verified:
            return {
                'status': 'verified',
                'label': _('موثق'),
                'class': 'success',
                'icon': 'bi-patch-check-fill'
            }
        elif self.id_document:
            return {
                'status': 'pending',
                'label': _('قيد المراجعة'),
                'class': 'warning',
                'icon': 'bi-clock-fill'
            }
        else:
            return {
                'status': 'unverified',
                'label': _('غير موثق'),
                'class': 'secondary',
                'icon': 'bi-exclamation-circle-fill'
            }
    
    # User Type Helper Methods
    def is_customer(self):
        """هل المستخدم عميل؟"""
        return self.user_type == self.UserType.CUSTOMER
    
    def is_provider(self):
        """هل المستخدم مقدم خدمة؟"""
        return self.user_type == self.UserType.PROVIDER
    
    def is_admin(self):
        """هل المستخدم مدير؟"""
        return self.user_type == self.UserType.ADMIN
    
    def can_create_services(self):
        """هل يمكن للمستخدم إنشاء خدمات؟"""
        if self.is_provider():
            return self.provider_approved
        return self.is_admin()
    
    def save(self, *args, **kwargs):
        # تحديث نسبة الاكتمال قبل الحفظ
        self.completion_percentage = self.calculate_completion()
        self.profile_completed = self.completion_percentage >= 80
        super().save(*args, **kwargs)


# ============================================================================
# Provider Agreement Models - نماذج التعهدات القانونية
# ============================================================================

class ProviderAgreement(models.Model):
    """
    تعهد وإقرار مقدم الخدمة - Legal Agreement
    """
    provider = models.OneToOneField(
        Provider,
        on_delete=models.CASCADE,
        related_name='agreement',
        verbose_name=_('مقدم الخدمة')
    )
    # معلومات التعهد
    full_name = models.CharField(
        max_length=200,
        verbose_name=_('الاسم الكامل')
    )
    national_id = models.CharField(
        max_length=50,
        verbose_name=_('رقم البطاقة الموحدة')
    )
    address = models.TextField(
        verbose_name=_('عنوان السكن الكامل')
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^(\+964|0)?7[3-9]\d{8}$',
            message='يرجى إدخال رقم هاتف عراقي صحيح'
        )],
        verbose_name=_('رقم الهاتف')
    )
    specialty = models.CharField(
        max_length=200,
        verbose_name=_('التخصص المهني')
    )
    
    # الالتزامات
    conduct_agreement = models.BooleanField(
        default=False,
        verbose_name=_('الالتزام بالسلوك العام'),
        help_text='أتعهد بحسن السيرة والسلوك واحترام حرمة المنازل'
    )
    professional_standards = models.BooleanField(
        default=False,
        verbose_name=_('الالتزام بالمعايير المهنية'),
        help_text='أتعهد بالالتزام بقائمة الأسعار الثابتة وتقديم خدمة عالية الجودة'
    )
    commission_agreement = models.BooleanField(
        default=False,
        verbose_name=_('الالتزام المالي'),
        help_text='أقر بعمولة المنصة وعدم الاتفاق خارج المنصة'
    )
    privacy_agreement = models.BooleanField(
        default=False,
        verbose_name=_('سرية البيانات'),
        help_text='أتعهد بعدم استخدام بيانات العملاء لأغراض شخصية'
    )
    
    # العمولة
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        verbose_name=_('نسبة العمولة %')
    )
    commission_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('مبلغ العمولة الثابت (دينار)')
    )
    
    # الوثائق
    id_card_front = models.ImageField(
        upload_to='agreements/id_cards/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])],
        verbose_name=_('صورة البطاقة - الوجه الأمامي')
    )
    id_card_back = models.ImageField(
        upload_to='agreements/id_cards/%Y/%m/',
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'pdf'])],
        verbose_name=_('صورة البطاقة - الوجه الخلفي')
    )
    signature_image = models.ImageField(
        upload_to='agreements/signatures/%Y/%m/',
        blank=True,
        verbose_name=_('صورة التوقيع')
    )
    thumbprint_image = models.ImageField(
        upload_to='agreements/thumbprints/%Y/%m/',
        blank=True,
        verbose_name=_('صورة بصمة الإبهام')
    )
    
    # التوقيع والتاريخ
    signed_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('تاريخ التوقيع')
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_agreements',
        verbose_name=_('تم التحقق بواسطة')
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ التحقق')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('ملاحظات الإدارة')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )
    
    class Meta:
        verbose_name = _('تعهد مقدم خدمة')
        verbose_name_plural = _('تعهدات مقدمي الخدمات')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'تعهد {self.full_name} - {self.provider.display_name}'
    
    def is_fully_signed(self):
        """هل تم توقيع جميع البنود؟"""
        return all([
            self.conduct_agreement,
            self.professional_standards,
            self.commission_agreement,
            self.privacy_agreement
        ])
    
    def get_commission_amount(self, service_price):
        """حساب مبلغ العمولة"""
        if self.commission_fixed > 0:
            return float(self.commission_fixed)
        return float(service_price) * float(self.commission_percentage) / 100


class ProviderViolation(models.Model):
    """
    مخالفات مقدم الخدمة
    """
    VIOLATION_TYPES = [
        ('conduct', 'مخالفة سلوكية'),
        ('quality', 'مخالفة جودة العمل'),
        ('pricing', 'مخالفة الأسعار'),
        ('commission', 'التهرب من العمولة'),
        ('privacy', 'انتهاك الخصوصية'),
        ('other', 'أخرى'),
    ]
    
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='violations',
        verbose_name=_('مقدم الخدمة')
    )
    violation_type = models.CharField(
        max_length=20,
        choices=VIOLATION_TYPES,
        verbose_name=_('نوع المخالفة')
    )
    description = models.TextField(
        verbose_name=_('وصف المخالفة')
    )
    severity = models.PositiveSmallIntegerField(
        choices=[(1, 'بسيطة'), (2, 'متوسطة'), (3, 'خطيرة')],
        default=1,
        verbose_name=_('درجة الخطورة')
    )
    evidence = models.FileField(
        upload_to='violations/%Y/%m/',
        blank=True,
        verbose_name=_('الدليل')
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_violations',
        verbose_name=_('المبلغ')
    )
    action_taken = models.TextField(
        blank=True,
        verbose_name=_('الإجراء المتخذ')
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name=_('تم الحل')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ التسجيل')
    )
    
    class Meta:
        verbose_name = _('مخالفة')
        verbose_name_plural = _('المخالفات')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_violation_type_display()} - {self.provider.display_name}'


# Signal لإنشاء UserProfile تلقائياً عند إنشاء User جديد
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """إنشاء ملف شخصي تلقائياً للمستخدم الجديد"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """حفظ الملف الشخصي عند حفظ المستخدم"""
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except (UserProfile.DoesNotExist, AttributeError):
        # في حال عدم وجود ملف شخصي أو وجود خطأ تقني، لا نفعل شيئاً
        # حيث سيتم التعامل معه في مكان آخر (مثل دالة save في النموذج)
        pass
