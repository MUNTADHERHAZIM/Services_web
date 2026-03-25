from django.contrib import admin
from .models import Review, ReviewImage, ReviewResponse


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    fields = ['image', 'caption']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'service', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['customer__username', 'service__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ReviewImageInline]
    
    fieldsets = (
        ('معلومات المراجعة', {
            'fields': ('service', 'customer', 'service_request')
        }),
        ('التقييم', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('الإدارة', {
            'fields': ('is_approved', 'created_at', 'updated_at')
        }),
    )


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'provider', 'created_at']
    search_fields = ['review__customer__username', 'provider__username', 'response_text']
    readonly_fields = ['created_at', 'updated_at']
