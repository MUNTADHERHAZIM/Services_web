"""
أمر إضافة تقييمات تجريبية
Add Sample Reviews Command
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import Service, Review


class Command(BaseCommand):
    help = 'إضافة تقييمات تجريبية للخدمات'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('جاري إضافة التقييمات التجريبية...'))
        
        try:
            customer1 = User.objects.get(username='customer1')
            customer2 = User.objects.get(username='customer2')
            customer3 = User.objects.get(username='customer3')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('خطأ: لم يتم العثور على العملاء'))
            return
        
        reviews_data = [
            {
                'service_slug': 'professional-logo-design',
                'customer': customer1,
                'rating': 5,
                'title': 'خدمة ممتازة واحترافية',
                'comment': 'أحمد مصمم موهوب وفاهم متطلبات العميل. الشعارexactly ما كنت أريده. أنصح به بشدة!',
                'pros': 'تصميم إبداعي، تعديلات سريعة، تواصل ممتاز',
                'cons': 'لا شيء، كل شيء كان مثالي',
                'is_verified_purchase': True
            },
            {
                'service_slug': 'professional-logo-design',
                'customer': customer2,
                'rating': 4,
                'title': 'شغل جميل',
                'comment': 'عمل جيد وتصميم جذاب. استغرق الأمر بعض الوقت لكن النتيجة تستحق.',
                'pros': 'جودة التصميم، الألوان متناسقة',
                'cons': 'التواصل كان بطيئاً أحياناً',
                'is_verified_purchase': True
            },
            {
                'service_slug': 'full-website-development',
                'customer': customer1,
                'rating': 5,
                'title': 'موقع رائع وبسرعة',
                'comment': 'علي مبرمج ممتاز. سلم الموقع قبل الموعد بثلاثة أيام وكل شيء يعمل بشكل ممتاز.',
                'pros': 'سرعة التسليم، كود نظيف، موقع متجاوب',
                'cons': '',
                'is_verified_purchase': True
            },
            {
                'service_slug': 'full-website-development',
                'customer': customer3,
                'rating': 5,
                'title': 'أفضل قرار',
                'comment': 'كنت متردد لكن علي أثبت أنه الأفضل. موقعي الآن يجلب لي عملاء جدد يومياً.',
                'pros': 'احترافية، صبر على التعديلات، دعم فني ممتاز',
                'cons': '',
                'is_verified_purchase': True
            },
            {
                'service_slug': 'social-media-management',
                'customer': customer2,
                'rating': 4,
                'title': 'فاطمة شغلة كويس',
                'comment': 'فاطمة فهمة工作量 ومحتوى منشوراتها يجذب المتابعين. نسبة التفاعل زادت 40%.',
                'pros': 'محتوى إبداعي، منشورات منتظمة، تقارير مفصلة',
                'cons': 'كنت أريد أكثر من 20 منشور شهرياً',
                'is_verified_purchase': True
            },
            {
                'service_slug': 'mobile-app-development',
                'customer': customer1,
                'rating': 5,
                'title': 'تطبيق أحلام变成了 حقيقة',
                'comment': 'علي حول فكرة التطبيق إلى حقيقة. التطبيق سهل الاستخدام وجميل. شكراً جزيلاً!',
                'pros': 'تصميم جميل، تطبيق سريع، دعم ممتاز',
                'cons': '',
                'is_verified_purchase': False
            },
            {
                'service_slug': 'complete-brand-identity',
                'customer': customer3,
                'rating': 5,
                'title': 'هوية بصرية متميزة',
                'comment': 'فريق أحمد فهم رؤيتي بشكل كامل. الهوية البصرية الآن جزء أساسي من نجاح شركتي.',
                'pros': 'شمولية الخدمة، تفاصيل دقيقة، ملفات جاهزة للاستخدام',
                'cons': '',
                'is_verified_purchase': True
            },
            {
                'service_slug': 'promotional-video',
                'customer': customer2,
                'rating': 4,
                'title': 'فيديو جميل',
                'comment': 'حسن مصور موهوب. الفيديو كان جيد لكنتاج أح تعديلات إضافية.',
                'pros': 'تصوير احترافي، جودة عالية',
                'cons': 'احتاج تعديلات أكثر',
                'is_verified_purchase': True
            },
        ]
        
        added_count = 0
        for r_data in reviews_data:
            try:
                service = Service.objects.get(slug=r_data['service_slug'])
                
                # التحقق من عدم وجود تقييم مسبق
                if not Review.objects.filter(service=service, customer=r_data['customer']).exists():
                    Review.objects.create(
                        service=service,
                        customer=r_data['customer'],
                        rating=r_data['rating'],
                        title=r_data['title'],
                        comment=r_data['comment'],
                        pros=r_data.get('pros', ''),
                        cons=r_data.get('cons', ''),
                        is_verified_purchase=r_data.get('is_verified_purchase', False),
                        is_approved=True
                    )
                    added_count += 1
                    self.stdout.write(f'✓ تم إضافة تقييم لـ {service.title}')
                else:
                    self.stdout.write(f'- تكرار: {service.title} - {r_data["customer"].username}')
            except Service.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'خطأ: الخدمة {r_data["service_slug"]} غير موجودة'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ تم إضافة {added_count} تقييم تجريبي'))
