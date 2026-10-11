from django.contrib import admin
from .models import ServiceView, SearchAnalytics, ProviderStats


@admin.register(ServiceView)
class ServiceViewAdmin(admin.ModelAdmin):
    list_display = ("service", "user", "device_type", "country", "viewed_at")
    list_filter = ("device_type", "country", "viewed_at")
    search_fields = ("service__title", "user__username", "ip_address")
    raw_id_fields = ("service", "user")


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "query",
        "search_count",
        "results_count_avg",
        "clicks_count",
        "conversion_count",
    )
    search_fields = ("query",)


@admin.register(ProviderStats)
class ProviderStatsAdmin(admin.ModelAdmin):
    list_display = (
        "provider",
        "total_earnings",
        "available_balance",
        "total_orders",
        "completion_rate",
    )
    search_fields = ("provider__user__username",)
    raw_id_fields = ("provider",)
