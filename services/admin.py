"""
Services Admin - لوحة إدارة الخدمات
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Category, Tag, Service, ServiceImage, Review, ServicePackage, ServiceFeature, ServiceFAQ, ProviderPortfolio, Testimonial


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """إدارة التصنيفات"""
    list_display = ['name', 'slug', 'icon_preview', 'services_count', 'is_active_badge', 'order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'slug', 'description')
        }),
        ('المظهر', {
            'fields': ('icon', 'image')
        }),
        ('الإعدادات', {
            'fields': ('is_active', 'order')
        }),
    )

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
        return '-'
    icon_preview.short_description = 'الأيقونة'

    def services_count(self, obj):
        count = obj.get_services_count()
        return format_html('<span class="badge bg-info">{}</span>', count)
    services_count.short_description = 'عدد الخدمات'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge bg-success">نشط</span>')
        return format_html('<span class="badge bg-danger">غير نشط</span>')
    is_active_badge.short_description = 'الحالة'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """إدارة الوسوم"""
    list_display = ['name', 'slug', 'services_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def services_count(self, obj):
        return obj.services.count()
    services_count.short_description = 'عدد الخدمات'


class ServiceImageInline(admin.TabularInline):
    """صور الخدمة داخل صفحة الخدمة"""
    model = ServiceImage
    extra = 1
    fields = ['image', 'caption', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'معاينة'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """إدارة الخدمات"""
    list_display = [
        'title', 'category', 'provider', 'price_display', 
        'is_active_badge', 'is_featured_badge', 'views_count', 
        'avg_rating_display', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'summary', 'description', 'provider__display_name']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'avg_rating', 'created_at', 'updated_at', 'cover_preview']
    date_hierarchy = 'created_at'
    inlines = [ServiceImageInline]
    save_on_top = True
    list_per_page = 20

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'slug', 'category', 'provider')
        }),
        ('المحتوى', {
            'fields': ('summary', 'description')
        }),
        ('السعر والمدة', {
            'fields': ('price', 'price_note', 'duration')
        }),
        ('الوسائط', {
            'fields': ('cover_image', 'cover_preview')
        }),
        ('التصنيف والوسوم', {
            'fields': ('tags',)
        }),
        ('الإعدادات', {
            'fields': ('is_active', 'is_featured')
        }),
        ('الإحصائيات', {
            'fields': ('views_count', 'avg_rating'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px; border-radius: 8px;" />', 
                obj.cover_image.url
            )
        return 'لا توجد صورة'
    cover_preview.short_description = 'معاينة الغلاف'

    def price_display(self, obj):
        return obj.get_display_price()
    price_display.short_description = 'السعر'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge bg-success">نشط</span>')
        return format_html('<span class="badge bg-danger">غير نشط</span>')
    is_active_badge.short_description = 'الحالة'

    def is_featured_badge(self, obj):
        if obj.is_featured:
            return format_html('<span class="badge bg-warning text-dark">⭐ مميز</span>')
        return '-'
    is_featured_badge.short_description = 'مميز'

    def avg_rating_display(self, obj):
        if obj.avg_rating > 0:
            stars = '⭐' * int(obj.avg_rating)
            return format_html('{} ({})', stars, obj.avg_rating)
        return '-'
    avg_rating_display.short_description = 'التقييم'

    actions = ['activate_services', 'deactivate_services', 'feature_services', 'unfeature_services']

    @admin.action(description='تفعيل الخدمات المحددة')
    def activate_services(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'تم تفعيل {updated} خدمة.')

    @admin.action(description='تعطيل الخدمات المحددة')
    def deactivate_services(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'تم تعطيل {updated} خدمة.')

    @admin.action(description='تمييز الخدمات المحددة')
    def feature_services(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'تم تمييز {updated} خدمة.')

    @admin.action(description='إلغاء تمييز الخدمات المحددة')
    def unfeature_services(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'تم إلغاء تمييز {updated} خدمة.')


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    """إدارة صور الخدمات"""
    list_display = ['service', 'image_preview', 'caption', 'order']
    list_filter = ['service__category']
    search_fields = ['service__title', 'caption']
    list_editable = ['order'] if False else []

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px; border-radius: 4px;" />', 
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'معاينة'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """إدارة التقييمات"""
    list_display = ['service', 'customer', 'rating_display', 'is_approved_badge', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['service__title', 'customer__username', 'comment']
    autocomplete_fields = ['service', 'customer']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def rating_display(self, obj):
        return '⭐' * obj.rating
    rating_display.short_description = 'التقييم'

    def is_approved_badge(self, obj):
        if obj.is_approved:
            return format_html('<span class="badge bg-success">معتمد</span>')
        return format_html('<span class="badge bg-warning text-dark">في الانتظار</span>')
    is_approved_badge.short_description = 'الحالة'

    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description='اعتماد التقييمات المحددة')
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'تم اعتماد {updated} تقييم.')

    @admin.action(description='رفض التقييمات المحددة')
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'تم رفض {updated} تقييم.')


# ============================================================================
# New Professional Models Admin
# ============================================================================

class ServicePackageInline(admin.TabularInline):
    """باقات الخدمة داخل صفحة الخدمة"""
    model = ServicePackage
    extra = 1
    fields = ['name', 'package_type', 'price', 'duration_days', 'revision_count', 'is_active', 'order']


class ServiceFeatureInline(admin.TabularInline):
    """مميزات الخدمة داخل صفحة الخدمة"""
    model = ServiceFeature
    extra = 1
    fields = ['title', 'description', 'icon', 'order']


class ServiceFAQInline(admin.TabularInline):
    """الأسئلة الشائعة داخل صفحة الخدمة"""
    model = ServiceFAQ
    extra = 1
    fields = ['question', 'answer', 'order', 'is_active']


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    """إدارة باقات الخدمات"""
    list_display = ['service', 'name', 'package_type', 'price', 'duration_days', 'is_active', 'order']
    list_filter = ['package_type', 'is_active']
    search_fields = ['name', 'service__title']
    autocomplete_fields = ['service']


@admin.register(ServiceFeature)
class ServiceFeatureAdmin(admin.ModelAdmin):
    """إدارة مميزات الخدمات"""
    list_display = ['service', 'title', 'icon', 'order']
    list_filter = ['service__category']
    search_fields = ['title', 'service__title']
    autocomplete_fields = ['service']


@admin.register(ServiceFAQ)
class ServiceFAQAdmin(admin.ModelAdmin):
    """إدارة الأسئلة الشائعة"""
    list_display = ['service', 'question', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['question', 'answer', 'service__title']
    autocomplete_fields = ['service']


@admin.register(ProviderPortfolio)
class ProviderPortfolioAdmin(admin.ModelAdmin):
    """إدارة معرض الأعمال"""
    list_display = ['provider', 'title', 'client_name', 'completion_date', 'is_featured', 'order']
    list_filter = ['is_featured', 'completion_date']
    search_fields = ['title', 'client_name', 'provider__display_name']
    autocomplete_fields = ['provider']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """إدارة شهادات العملاء"""
    list_display = ['service', 'customer_name', 'rating', 'is_featured', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_approved']
    search_fields = ['customer_name', 'comment', 'service__title']
    autocomplete_fields = ['service']

    def rating_display(self, obj):
        return '⭐' * obj.rating
    rating_display.short_description = 'التقييم'
