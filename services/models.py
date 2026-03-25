"""
Services Models - نماذج الخدمات
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from accounts.models import Provider


class Category(models.Model):
    """
    تصنيف الخدمات
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('اسم التصنيف')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
        verbose_name=_('الرابط المختصر')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('الوصف')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('اسم أيقونة Bootstrap مثل: bi-laptop'),
        verbose_name=_('الأيقونة')
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name=_('الصورة')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )

    class Meta:
        verbose_name = _('تصنيف')
        verbose_name_plural = _('التصنيفات')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('services:category_detail', kwargs={'slug': self.slug})

    def get_services_count(self):
        """عدد الخدمات في التصنيف"""
        return self.services.filter(is_active=True).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """
    وسوم الخدمات
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_('اسم الوسم')
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        allow_unicode=True,
        verbose_name=_('الرابط المختصر')
    )

    class Meta:
        verbose_name = _('وسم')
        verbose_name_plural = _('الوسوم')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Service(models.Model):
    """
    الخدمة
    """
    class Status(models.TextChoices):
        DRAFT = 'draft', _('مسودة')
        ACTIVE = 'active', _('نشط')
        INACTIVE = 'inactive', _('غير نشط')
        ARCHIVED = 'archived', _('مؤرشف')
    
    class Level(models.TextChoices):
        BEGINNER = 'beginner', _('مبتدئ')
        INTERMEDIATE = 'intermediate', _('متوسط')
        EXPERT = 'expert', _('خبير')
        PROFESSIONAL = 'professional', _('محترف')
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='services',
        verbose_name=_('التصنيف')
    )
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('مقدم الخدمة')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان الخدمة')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        allow_unicode=True,
        verbose_name=_('الرابط المختصر')
    )
    summary = models.CharField(
        max_length=300,
        verbose_name=_('ملخص قصير')
    )
    description = models.TextField(
        verbose_name=_('الوصف التفصيلي')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_('الحالة')
    )
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.INTERMEDIATE,
        verbose_name=_('المستوى')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('السعر')
    )
    price_note = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('مثال: يبدأ من، حسب الطلب'),
        verbose_name=_('ملاحظة السعر')
    )
    duration = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('مثال: 3-5 أيام عمل'),
        verbose_name=_('مدة التنفيذ')
    )
    cover_image = models.ImageField(
        upload_to='services/covers/',
        blank=True,
        null=True,
        verbose_name=_('صورة الغلاف')
    )
    video_intro = models.URLField(
        blank=True,
        verbose_name=_('رابط الفيديو التعريفي'),
        help_text=_('رابط يوتيوب أو Vimeo')
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='services',
        verbose_name=_('الوسوم')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('مميز')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('خدمة موثقة')
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد المشاهدات')
    )
    orders_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد الطلبات')
    )
    avg_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        verbose_name=_('متوسط التقييم')
    )
    total_reviews = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد التقييمات')
    )
    response_time = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('وقت الاستجابة'),
        help_text=_('مثال: خلال ساعة واحدة')
    )
    delivery_time = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('مدة التسليم')
    )
    revision_count = models.PositiveIntegerField(
        default=1,
        verbose_name=_('عدد المراجعات')
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
        verbose_name = _('خدمة')
        verbose_name_plural = _('الخدمات')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """زيادة عدد المشاهدات"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def get_display_price(self):
        """عرض السعر بشكل مناسب"""
        if self.price:
            if self.price_note:
                return f"{self.price_note}: {self.price} ر.س"
            return f"{self.price} ر.س"
        return "حسب الطلب"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
            # التأكد من أن الـ slug فريد
            original_slug = self.slug
            counter = 1
            while Service.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class ServiceImage(models.Model):
    """
    صور الخدمة
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('الخدمة')
    )
    image = models.ImageField(
        upload_to='services/images/',
        verbose_name=_('الصورة')
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('وصف الصورة')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب')
    )

    class Meta:
        verbose_name = _('صورة خدمة')
        verbose_name_plural = _('صور الخدمات')
        ordering = ['order']

    def __str__(self):
        return f"صورة {self.service.title}"


class Review(models.Model):
    """
    تقييمات الخدمات (Phase 2)
    تقييم الخدمة - نظام محسّن واحترافي
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('الخدمة')
    )
    customer = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='service_reviews',
        verbose_name=_('العميل')
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        verbose_name=_('التقييم')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان التقييم'),
        help_text=_('مثال: خدمة ممتازة وسريعة')
    )
    comment = models.TextField(
        verbose_name=_('التعليق')
    )
    pros = models.TextField(
        blank=True,
        verbose_name=_('الإيجابيات'),
        help_text=_('ما هي مميزات هذه الخدمة؟')
    )
    cons = models.TextField(
        blank=True,
        verbose_name=_('السلبيات'),
        help_text=_('ما هي النقاط التي تحتاج لتحسين؟')
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        verbose_name=_('شراء موثق'),
        help_text=_('هل العميل طلب الخدمة فعلياً؟')
    )
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('عدد المفيد'),
        help_text=_('عدد من وجد هذا التقييم مفيداً')
    )
    # رد مقدم الخدمة
    provider_response = models.TextField(
        blank=True,
        verbose_name=_('رد مقدم الخدمة')
    )
    provider_response_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الرد')
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name=_('موافق عليه'),
        help_text=_('هل تم مراجعة والموافقة على التقييم؟')
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
        verbose_name = _('تقييم')
        verbose_name_plural = _('التقييمات')
        ordering = ['-created_at']
        # عميل واحد يمكنه تقييم الخدمة مرة واحدة
        unique_together = ['service', 'customer']

    def __str__(self):
        return f'{self.customer.username} - {self.service.title} ({self.rating}⭐)'

    def get_rating_stars(self):
        """عرض التقييم كنجوم"""
        return '⭐' * self.rating + '☆' * (5 - self.rating)
    
    def get_rating_percentage(self):
        """نسبة التقييم من 100"""
        return (self.rating / 5) * 100
    
    def mark_helpful(self):
        """زيادة عداد المفيد"""
        self.helpful_count += 1
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # تحديث متوسط التقييم للخدمة
        self.update_service_rating()

    def update_service_rating(self):
        """تحديث متوسط تقييم الخدمة"""
        from django.db.models import Avg
        avg = self.service.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        self.service.avg_rating = round(avg, 1) if avg else 0
        self.service.save(update_fields=['avg_rating'])


# ============================================================================
# Professional Service Add-ons - إضافات الخدمة الاحترافية
# ============================================================================

class ServicePackage(models.Model):
    """
    باقات الخدمة - Service Packages
    """
    class PackageType(models.TextChoices):
        BASIC = 'basic', _('أساسي')
        STANDARD = 'standard', _('قياسي')
        PREMIUM = 'premium', _('ممتاز')
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='packages',
        verbose_name=_('الخدمة')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('اسم الباقة')
    )
    package_type = models.CharField(
        max_length=20,
        choices=PackageType.choices,
        default=PackageType.BASIC,
        verbose_name=_('نوع الباقة')
    )
    description = models.TextField(
        verbose_name=_('وصف الباقة')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('السعر')
    )
    duration_days = models.PositiveIntegerField(
        default=1,
        verbose_name=_('مدة التسليم (أيام)')
    )
    revision_count = models.PositiveIntegerField(
        default=1,
        verbose_name=_('عدد المراجعات')
    )
    features = models.JSONField(
        default=list,
        verbose_name=_('المميزات'),
        help_text=_('قائمة المميزات كـ JSON')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    class Meta:
        verbose_name = _('باقة خدمة')
        verbose_name_plural = ('باقات الخدمات')
        ordering = ['order', 'price']
    
    def __str__(self):
        return f"{self.name} - {self.service.title}"
    
    def get_features_list(self):
        """إرجاع المميزات كقائمة"""
        if isinstance(self.features, list):
            return self.features
        return []


class ServiceFeature(models.Model):
    """
    مميزات الخدمة - Service Features
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name=_('الخدمة')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان الميزة')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('وصف الميزة')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('الأيقونة'),
        help_text=_('اسم أيقونة Bootstrap Icons')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب')
    )
    
    class Meta:
        verbose_name = _('ميزة خدمة')
        verbose_name_plural = ('مميزات الخدمات')
        ordering = ['order']
    
    def __str__(self):
        return self.title


class ServiceFAQ(models.Model):
    """
    الأسئلة الشائعة للخدمة - Service FAQs
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='faqs',
        verbose_name=_('الخدمة')
    )
    question = models.CharField(
        max_length=300,
        verbose_name=_('السؤال')
    )
    answer = models.TextField(
        verbose_name=_('الجواب')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    class Meta:
        verbose_name = _('سؤال شائع')
        verbose_name_plural = ('الأسئلة الشائعة')
        ordering = ['order']
    
    def __str__(self):
        return self.question


class ProviderPortfolio(models.Model):
    """
    معرض أعمال مقدم الخدمة - Provider Portfolio
    """
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name='portfolio_items',
        verbose_name=_('مقدم الخدمة')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان العمل')
    )
    description = models.TextField(
        verbose_name=_('وصف العمل')
    )
    image = models.ImageField(
        upload_to='portfolio/',
        verbose_name=_('الصورة')
    )
    link = models.URLField(
        blank=True,
        verbose_name=_('رابط العمل')
    )
    client_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('اسم العميل')
    )
    completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('تاريخ الإنجاز')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('مميز')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('الترتيب')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    class Meta:
        verbose_name = _('عمل في المعرض')
        verbose_name_plural = ('معرض الأعمال')
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """
    شهادات العملاء - Customer Testimonials
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='testimonials',
        verbose_name=_('الخدمة')
    )
    customer_name = models.CharField(
        max_length=100,
        verbose_name=_('اسم العميل')
    )
    customer_avatar = models.ImageField(
        upload_to='testimonials/avatars/',
        blank=True,
        null=True,
        verbose_name=_('صورة العميل')
    )
    customer_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('المسمى الوظيفي')
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        default=5,
        verbose_name=_('التقييم')
    )
    comment = models.TextField(
        verbose_name=_('التعليق')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('مميز')
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name=_('موافق عليه')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    class Meta:
        verbose_name = _('شهادة عميل')
        verbose_name_plural = ('شهادات العملاء')
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"شهادة من {self.customer_name}"
    
    def get_rating_stars(self):
        """عرض التقييم كنجوم"""
        return '★' * self.rating + '☆' * (5 - self.rating)
