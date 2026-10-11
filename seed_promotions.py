import os
import django
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import PromotionalBanner, Coupon
from services.models import Service

print("Creating/updating promotional banners...")
# 1. Announcement banner
announcement, created = PromotionalBanner.objects.get_or_create(
    banner_type=PromotionalBanner.BannerType.ANNOUNCEMENT,
    title="🎉 عروض الموسم الحصرية: احصل على خصم 20% على كافة الخدمات باستخدام الكوبون PROMO20",
    defaults={
        'subtitle': 'لفترة محدودة',
        'badge_text': 'خصم خاص 🔥',
        'cta_text': 'نسخ الكود وتصفح العروض',
        'cta_url': '/services/?deals=true',
        'coupon_code': 'PROMO20',
        'bg_gradient': 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
        'is_active': True,
        'order': 1,
    }
)
if not created:
    announcement.is_active = True
    announcement.save()
print(f"Announcement banner: {announcement.title} (Active: {announcement.is_active})")

# 2. Promo cards
card1, _ = PromotionalBanner.objects.get_or_create(
    banner_type=PromotionalBanner.BannerType.PROMO_CARD,
    title="باقات التصميم والتطوير البرمجي الاحترافي",
    defaults={
        'subtitle': 'ارتقِ بمشروعك الرقمي مع نخبة الخبراء والمستقلين المعتمدين بخصومات تصل حتى 35%!',
        'badge_text': 'عرض حصري ⚡',
        'cta_text': 'استكشف العروض الآن',
        'cta_url': '/services/?deals=true',
        'coupon_code': 'PROMO20',
        'bg_gradient': 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%)',
        'is_active': True,
        'order': 1,
    }
)
card1.is_active = True
card1.save()

card2, _ = PromotionalBanner.objects.get_or_create(
    banner_type=PromotionalBanner.BannerType.PROMO_CARD,
    title="كوبون ترحيبي 15% لطلبك القادم",
    defaults={
        'subtitle': 'استخدم الكود WELCOME15 عند إتمام الطلب واحصل على توفير فوري ومباشر على فاتورتك.',
        'badge_text': 'هدية ترحيبية 🎁',
        'cta_text': 'تصفح كافة الخدمات',
        'cta_url': '/services/',
        'coupon_code': 'WELCOME15',
        'bg_gradient': 'linear-gradient(135deg, #064e3b 0%, #047857 50%, #059669 100%)',
        'is_active': True,
        'order': 2,
    }
)
card2.is_active = True
card2.save()
print("Promo banners ready.")

# 3. Coupons
print("Creating coupons...")
c1, _ = Coupon.objects.get_or_create(
    code='PROMO20',
    defaults={
        'description': 'خصم 20% على العروض الخاصة وجميع الخدمات المؤهلة',
        'discount_type': Coupon.DiscountType.PERCENTAGE,
        'discount_value': Decimal('20.00'),
        'min_order_amount': Decimal('30.00'),
        'max_discount_amount': Decimal('100.00'),
        'max_uses': 500,
        'valid_from': timezone.now() - timedelta(days=1),
        'valid_until': timezone.now() + timedelta(days=30),
        'is_active': True,
    }
)
c1.is_active = True
c1.save()

c2, _ = Coupon.objects.get_or_create(
    code='WELCOME15',
    defaults={
        'description': 'كوبون ترحيبي بخصم 15% للطلبات بحد أدنى 20 دولار',
        'discount_type': Coupon.DiscountType.PERCENTAGE,
        'discount_value': Decimal('15.00'),
        'min_order_amount': Decimal('20.00'),
        'max_discount_amount': Decimal('50.00'),
        'max_uses': 1000,
        'valid_from': timezone.now() - timedelta(days=1),
        'valid_until': timezone.now() + timedelta(days=60),
        'is_active': True,
    }
)
c2.is_active = True
c2.save()

c3, _ = Coupon.objects.get_or_create(
    code='SAVE50',
    defaults={
        'description': 'خصم ثابت بقيمة 50 دولار للطلبات فوق 150 دولار',
        'discount_type': Coupon.DiscountType.FIXED,
        'discount_value': Decimal('50.00'),
        'min_order_amount': Decimal('150.00'),
        'max_uses': 100,
        'valid_from': timezone.now() - timedelta(days=1),
        'valid_until': timezone.now() + timedelta(days=15),
        'is_active': True,
    }
)
c3.is_active = True
c3.save()
print("Coupons ready.")

# 4. Update services with discounts
services = Service.objects.filter(is_active=True)[:4]
future_date = timezone.now() + timedelta(days=7, hours=14, minutes=30)
for idx, svc in enumerate(services):
    if svc.price > 0:
        svc.original_price = Decimal(str(round(float(svc.price) * 1.35, 2)))
        svc.discount_end_date = future_date
        svc.save()
        print(f"Service '{svc.title}' updated: Original ${svc.original_price} -> Current ${svc.price} (Saving: {svc.discount_percentage}%)")

print("Seed data creation finished successfully!")
