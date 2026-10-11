import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category, Service, Tag
from accounts.models import Provider

print("Setting existing services 13, 14, 15 to USD...")
for s in Service.objects.filter(id__in=[13, 14, 15]):
    s.currency = 'USD'
    s.save()
    print(f"Service {s.id}: {s.title[:25]} set to USD ($ {s.price})")

# Check provider
provider = Provider.objects.filter(is_active=True).first()
if not provider:
    print("No active provider found!")
    exit()

print(f"Using provider: {provider.display_name}")

# Fetch or verify categories
home_cat = Category.objects.filter(name__icontains='صيانة').first()
car_cat = Category.objects.filter(name__icontains='سيارات').first()
tech_cat = Category.objects.filter(name__icontains='برمجة').first()
design_cat = Category.objects.filter(name__icontains='تصميم').first()

iraq_services = [
    {
        'title': 'صيانة وتنظيف وغسيل مكيفات وسبالت في البصرة مع تعبئة غاز أصلي',
        'category': home_cat,
        'summary': 'خدمة صيانة وغسيل أجهزة التكييف والسبالت وضبط الفريون بكفاءة عالية وضمان للعمل في منازل وشركات البصرة.',
        'description': 'نقدم لكم أفضل خدمات التبريد والتكييف في محافظة البصرة وضواحيها. فحص شامل للضاغط (الكومبريسور)، تنظيف الفلاتر والوحدة الخارجية والداخلية بمعدات الضغط العالي، فحص تسريب الغاز وتعبئة غاز R22 أو R410 الأصلي مع كفالة.',
        'price': Decimal('35000.00'),
        'original_price': Decimal('50000.00'),
        'currency': 'IQD',
        'price_note': 'للسبلت الواحد مع الفحص',
        'duration': 'خلال يوم واحد',
        'is_featured': True,
        'is_active': True,
        'discount_end_date': timezone.now() + timedelta(days=15),
    },
    {
        'title': 'تأسيس وصيانة كهرباء المنازل والمحلات وفحص لوحات القواطع الذكية',
        'category': home_cat,
        'summary': 'كهربائي محترف لتمديد الأسلاك، تركيب الإنارة المخفية والسبوت لايت، وإصلاح كافة الأعطال والتسريب الكهربائي.',
        'description': 'خدمات كهرباء متكاملة تشمل صيانة الأعطال الطارئة، تمديد خطوط السحب والمولدات، موازنة الأحمال على الفيزات الثلاثية، وتركيب منظمات الجهد لحماية الأجهزة المنزلية الحساسة.',
        'price': Decimal('25000.00'),
        'original_price': Decimal('35000.00'),
        'currency': 'IQD',
        'price_note': 'كشفية وزيارة الموقع',
        'duration': 'نفس اليوم',
        'is_featured': False,
        'is_active': True,
    },
    {
        'title': 'صيانة وتصليح السباكة المنزلية وكشف التسربات وتركيب المضخات والخزانات',
        'category': home_cat,
        'summary': 'سباك صحي خبير لحل مشاكل انسداد المجاري وتركيب أطقم الحمامات والمطابخ والخلاطات بقطع غيار أصلية.',
        'description': 'تنفيذ كافة أعمال التأسيسات الصحية، فحص ضغط المياه، صيانة السخانات الشمسية والكهربائية، تركيب فلاتر تحلية المياه (RO)، وتمديد شبكات الأنابيب الحرارية المقاومة.',
        'price': Decimal('30000.00'),
        'original_price': None,
        'currency': 'IQD',
        'price_note': 'أجور العمل حسب نوع العطل',
        'duration': 'ساعات معدودة',
        'is_featured': False,
        'is_active': True,
    },
    {
        'title': 'فحص كمبيوتر وبرمجة حساسات السيارات الحديثة في موقعك بالبصرة',
        'category': car_cat or home_cat,
        'summary': 'فحص شامل لكمبيوتر السيارة ومسح الأكواد وفحص بطارية الهايبرد والمحرك بواسطة أحدث أجهزة OBD2 المتطورة.',
        'description': 'نوفر خدمة فحص السيارات المتنقلة أينما كنت في البصرة. تقرير تفصيلي بأعطال الكير والمحرك والوسائد الهوائية (Airbags) ونظام مانع الانزلاق (ABS).',
        'price': Decimal('40000.00'),
        'original_price': Decimal('60000.00'),
        'currency': 'IQD',
        'price_note': 'فحص كامل مع التقرير المطبوع',
        'duration': 'ساعة واحدة',
        'is_featured': True,
        'is_active': True,
        'discount_end_date': timezone.now() + timedelta(days=10),
    },
    {
        'title': 'تطوير متجر إلكتروني متكامل يدعم الدفع ببطاقات زين كاش وزين العراق وماستركارد',
        'category': tech_cat or home_cat,
        'summary': 'متجر إلكتروني احترافي مصمم خصيصاً للشركات والمتاجر العراقية مع ربط بوابات الدفع المحلية وشركات التوصيل.',
        'description': 'تصميم وبرمجة متجر إلكتروني عالي السرعة والأمان، لوحة تحكم باللغة العربية، إدارة المنتجات والمخزون، تقارير المبيعات، ونظام إشعارات واتساب الفورية للطلبات الجديدة.',
        'price': Decimal('250.00'),
        'original_price': Decimal('350.00'),
        'currency': 'USD',
        'price_note': 'شامل الاستضافة والدومين لعام كامل',
        'duration': '7-10 أيام',
        'is_featured': True,
        'is_active': True,
        'discount_end_date': timezone.now() + timedelta(days=20),
    }
]

for data in iraq_services:
    cat = data.pop('category')
    title = data['title']
    service, created = Service.objects.get_or_create(
        title=title,
        defaults={
            'provider': provider,
            'category': cat,
            **data
        }
    )
    if not created:
        for k, v in data.items():
            setattr(service, k, v)
        if cat:
            service.category = cat
        service.save()
    print(f"Service {'created' if created else 'updated'}: {service.title[:30]} | {service.get_display_price()} ({service.currency})")

print("Seeding completed successfully!")
