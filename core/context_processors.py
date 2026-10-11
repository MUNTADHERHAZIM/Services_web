"""
Core Context Processors - معالجات السياق الشامل للمنصة
"""

from django.conf import settings
from django.db import models


def site_settings(request):
    """إضافة إعدادات الموقع ومعلومات المستخدم والعملة والمطور للسياق العام"""
    user_currency = request.session.get('user_currency', 'IQD')
    if user_currency not in ['IQD', 'USD']:
        user_currency = 'IQD'

    context = {
        'SITE_NAME': 'خدماتي - المنصة الاحترافية للخدمات المصغرة',
        'SITE_DESCRIPTION': 'منصة عراقية وعربية متكاملة لربط أفضل المستقلين ومقدمي الخدمات بالعملاء بالدينار العراقي والدولار',
        'DEBUG': settings.DEBUG,
        'user_currency': user_currency,
        'currency_symbol': 'د.ع' if user_currency == 'IQD' else '$',
        'currency_name': 'دينار عراقي' if user_currency == 'IQD' else 'دولار أمريكي',
        # معلومات مطور المنصة
        'DEVELOPER_NAME': 'MUNTADHER HAZIM',
        'DEVELOPER_NAME_AR': 'منتظر حاظم',
        'DEVELOPER_PHONE': '07724978301',
        'DEVELOPER_WHATSAPP': '9647724978301',
        'DEVELOPER_LOCATION': 'العراق - البصرة',
        'DEVELOPER_CITY': 'البصرة',
        'DEVELOPER_COUNTRY': 'العراق',
    }
    
    # تصنيفات شائعة لشريط التنقل
    try:
        from services.models import Category
        context['nav_categories'] = Category.objects.filter(
            is_active=True, 
            parent__isnull=True
        ).prefetch_related('subcategories').order_by('order', 'name')[:12]
    except Exception:
        context['nav_categories'] = []
    
    # إعلان أو عرض ترويجي نشط في الشريط العلوي
    try:
        from core.models import PromotionalBanner
        from django.utils import timezone
        now = timezone.now()
        context['active_announcement'] = PromotionalBanner.objects.filter(
            banner_type=PromotionalBanner.BannerType.ANNOUNCEMENT,
            is_active=True
        ).filter(
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=now)
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        ).order_by('order', '-created_at').first()
    except Exception:
        context['active_announcement'] = None
    
    if request.user.is_authenticated:
        try:
            from favorites.models import FavoriteService
            context['user_favorites_count'] = FavoriteService.objects.filter(user=request.user).count()
            context['user_favorite_ids'] = list(FavoriteService.objects.filter(user=request.user).values_list('service_id', flat=True))
        except Exception:
            context['user_favorites_count'] = 0
            context['user_favorite_ids'] = []
            
        try:
            from wallet.models import Wallet
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            context['user_wallet'] = wallet
        except Exception:
            context['user_wallet'] = None

        try:
            from conversations.models import Conversation
            unread_as_receiver = Conversation.objects.filter(receiver=request.user).aggregate(total=models.Sum('receiver_unread_count'))['total'] or 0
            unread_as_sender = Conversation.objects.filter(sender=request.user).aggregate(total=models.Sum('sender_unread_count'))['total'] or 0
            context['unread_messages_count'] = unread_as_receiver + unread_as_sender
        except Exception:
            context['unread_messages_count'] = 0
            
    return context
