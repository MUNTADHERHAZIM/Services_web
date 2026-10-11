import os
import django
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Provider
from services.models import Category, Service

provider = Provider.objects.first()
if not provider:
    print("No provider found!")
    exit(1)

dev_cat = Category.objects.filter(name__icontains='تطوير').first() or Category.objects.first()
design_cat = Category.objects.filter(name__icontains='تصميم').first() or Category.objects.first()
marketing_cat = Category.objects.filter(name__icontains='تسويق').first() or Category.objects.first()

future_date = timezone.now() + timedelta(days=5, hours=18, minutes=45)

services_data = [
    {
        'title': 'تصميم هوية بصرية كاملة وشعار احترافي للشركات والمشاريع',
        'slug': 'full-branding-logo-design-package',
        'category': design_cat,
        'summary': 'باقة تصميم متكاملة تشمل الشعار، لوحة الألوان، الخطوط، ونماذج المطبوعات مع تسليم كافة الملفات المصدرية المفتوحة.',
        'description': 'نقدم لك خدمة تصميم هوية بصرية متميزة تساعد علامتك التجارية على التميز والتأثير في السوق. يشمل العرض:\n1. تصميم 3 نماذج أولية للشعار.\n2. ملف الهوية البصرية (Brand Guidelines).\n3. تصميم كروت العمل والأوراق الرسمية.\n4. تسليم جميع الملفات بدقة عالية ومفتوحة المصدر AI, PSD, SVG, PDF.',
        'price': Decimal('75.00'),
        'original_price': Decimal('120.00'),
        'discount_end_date': future_date,
        'status': Service.Status.ACTIVE,
        'level': Service.Level.EXPERT,
        'duration': '3-4 أيام عمل',
        'price_note': 'خصم خاص 38%',
        'is_active': True,
        'is_featured': True,
        'views_count': 142,
        'orders_count': 28,
        'avg_rating': Decimal('4.9'),
        'total_reviews': 24,
    },
    {
        'title': 'تطوير موقع ويب تعريفي سريع ومتجاوب باستخدام Django و Bootstrap 5',
        'slug': 'responsive-django-website-development',
        'category': dev_cat,
        'summary': 'بناء وبرمجة موقع ويب احترافي، فائق السرعة ومتوافق مع جميع الهواتف الذكية مع لوحة تحكم سهلة لإدارة المحتوى.',
        'description': 'احصل على موقع إلكتروني احترافي لمشروعك أو شركتك يتمتع بأحدث المعايير البرمجية وأمان فائق:\n- تصميم واجهات أنيقة وعصرية.\n- لوحة تحكم مخصصة لإدارة الصفحات والأخبار.\n- تحسين سرعة التصفح وتوافق كامل مع محركات البحث (SEO).\n- حماية وأمان متقدم.',
        'price': Decimal('150.00'),
        'original_price': Decimal('220.00'),
        'discount_end_date': future_date,
        'status': Service.Status.ACTIVE,
        'level': Service.Level.PROFESSIONAL,
        'duration': '5-7 أيام عمل',
        'price_note': 'عرض نهاية الأسبوع',
        'is_active': True,
        'is_featured': True,
        'views_count': 210,
        'orders_count': 45,
        'avg_rating': Decimal('5.0'),
        'total_reviews': 39,
    },
    {
        'title': 'خطة تسويق رقمي وإدارة حملات إعلانية احترافية لزيادة المبيعات',
        'slug': 'digital-marketing-campaigns-strategy',
        'category': marketing_cat,
        'summary': 'استراتيجية تسويقية موجهة وإدارة حملات إعلانية ممولة على جوجل وميتا لزيادة العائد على الاستثمار ومضاعفة المبيعات.',
        'description': 'خطة إعلانية وتسويقية شاملة تتضمن:\n- دراسة المنافسين وتحديد الجمهور المستهدف بدقة.\n- إعداد وإنشاء الحملات الإعلانية على المنصات المناسبة.\n- كتابة نصوص الإعلانات التسويقية المؤثرة.\n- تقرير أسبوعي وتحليل دقيق للنتائج.',
        'price': Decimal('90.00'),
        'original_price': Decimal('130.00'),
        'discount_end_date': future_date,
        'status': Service.Status.ACTIVE,
        'level': Service.Level.INTERMEDIATE,
        'duration': '7 أيام عمل',
        'price_note': 'وفر 31%',
        'is_active': True,
        'is_featured': False,
        'views_count': 95,
        'orders_count': 19,
        'avg_rating': Decimal('4.8'),
        'total_reviews': 15,
    }
]

for data in services_data:
    svc, created = Service.objects.update_or_create(
        slug=data['slug'],
        defaults={
            **data,
            'provider': provider
        }
    )
    print(f"Service: {svc.title} -> Created={created}, Price=${svc.price}, Original=${svc.original_price}, Sale={svc.is_on_sale}, Discount={svc.discount_percentage}%")

print("Services successfully created/updated!")
