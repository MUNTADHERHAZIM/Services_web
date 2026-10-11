from django.contrib import admin
from .models import FavoriteService, RecentlyViewed, SearchHistory


@admin.register(FavoriteService)
class FavoriteServiceAdmin(admin.ModelAdmin):
    list_display = ("user", "service", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "service__title")
    raw_id_fields = ("user", "service")


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ("user", "service", "viewed_at")
    list_filter = ("viewed_at",)
    search_fields = ("user__username", "service__title")
    raw_id_fields = ("user", "service")


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "query", "results_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "query")
    raw_id_fields = ("user",)
