"""
Favorites Views - عروض المفضلة
"""

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from services.models import Service
from .models import FavoriteService


@login_required
@require_POST
def toggle_favorite(request, service_id):
    """تبديل حالة المفضلة لخدمة عبر AJAX"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    fav = FavoriteService.objects.filter(user=request.user, service=service).first()
    
    if fav:
        fav.delete()
        is_favorite = False
        message = "تمت إزالة الخدمة من المفضلة بنجاح"
    else:
        FavoriteService.objects.create(user=request.user, service=service)
        is_favorite = True
        message = "تمت إضافة الخدمة إلى قائمة مفضلتك بنجاح"
        
    return JsonResponse({
        "success": True,
        "is_favorite": is_favorite,
        "message": message,
        "total_favorites": FavoriteService.objects.filter(user=request.user).count()
    })


@method_decorator(login_required, name='dispatch')
class MyFavoritesView(ListView):
    """عرض قائمة الخدمات المفضلة للمستخدم"""
    model = FavoriteService
    template_name = 'favorites/my_favorites.html'
    context_object_name = 'favorites'
    paginate_by = 12

    def get_queryset(self):
        return FavoriteService.objects.filter(
            user=self.request.user
        ).select_related('service__category', 'service__provider__user')
