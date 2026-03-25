"""
أمر تحميل البيانات التجريبية
Load Sample Data Command
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from accounts.models import Provider
from services.models import Category, Tag, Service
from requests.models import ServiceRequest


class Command(BaseCommand):
    help = 'تحميل بيانات تجريبية للنظام'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('جاري تحميل البيانات التجريبية...'))
        
        # إنشاء المجموعات
        self.create_groups()
        
        # إنشاء المستخدمين
        self.create_users()
        
        # إنشاء التصنيفات
        self.create_categories()
        
        # إنشاء الوسوم
        self.create_tags()
        
        # إنشاء الخدمات
        self.create_services()
        
        # إنشاء طلبات تجريبية
        self.create_requests()
        
        self.stdout.write(self.style.SUCCESS('✓ تم تحميل البيانات التجريبية بنجاح!'))

    def create_groups(self):
        """إنشاء مجموعات المستخدمين"""
        groups = ['Staff', 'Provider', 'Customer']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
        self.stdout.write(f'✓ تم إنشاء {len(groups)} مجموعة')

    def create_users(self):
        """إنشاء مستخدمين تجريبيين"""
        # مدير النظام
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@services.iq',
                'first_name': 'مدير',
                'last_name': 'النظام',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        
        # موظف
        staff, created = User.objects.get_or_create(
            username='staff',
            defaults={
                'email': 'staff@services.iq',
                'first_name': 'موظف',
                'last_name': 'الإدارة',
                'is_staff': True
            }
        )
        if created:
            staff.set_password('staff123')
            staff.save()
            staff.groups.add(Group.objects.get(name='Staff'))
        
        # مقدمي الخدمات
        providers_data = [
            {
                'username': 'ahmed_designer',
                'email': 'ahmed@example.com',
                'first_name': 'أحمد',
                'last_name': 'المصمم',
                'display_name': 'أحمد للتصميم',
                'bio': 'مصمم جرافيك محترف خبرة 8 سنوات في تصميم الهويات البصرية والشعارات',
                'phone': '07701234567',
                'is_verified': True
            },
            {
                'username': 'ali_developer',
                'email': 'ali@example.com',
                'first_name': 'علي',
                'last_name': 'المبرمج',
                'display_name': 'علي للبرمجة',
                'bio': 'مطور ويب وتطبيقات موبايل، متخصص في Python و Flutter',
                'phone': '07702345678',
                'is_verified': True
            },
            {
                'username': 'fatima_marketing',
                'email': 'fatima@example.com',
                'first_name': 'فاطمة',
                'last_name': 'المسوقة',
                'display_name': 'فاطمة للتسويق',
                'bio': 'خبيرة تسويق رقمي ومحتوى، متخصصة في إدارة حملات السوشيال ميديا',
                'phone': '07703456789',
                'is_verified': True
            },
            {
                'username': 'hassan_photo',
                'email': 'hassan@example.com',
                'first_name': 'حسن',
                'last_name': 'المصور',
                'display_name': 'حسن للتصوير',
                'bio': 'مصور فوتوغرافي وفيديو محترف، متخصص في تصوير المناسبات والمنتجات',
                'phone': '07704567890',
                'is_verified': False
            },
        ]
        
        for p_data in providers_data:
            user, created = User.objects.get_or_create(
                username=p_data['username'],
                defaults={
                    'email': p_data['email'],
                    'first_name': p_data['first_name'],
                    'last_name': p_data['last_name']
                }
            )
            if created:
                user.set_password('provider123')
                user.save()
                user.groups.add(Group.objects.get(name='Provider'))
            
            Provider.objects.get_or_create(
                user=user,
                defaults={
                    'display_name': p_data['display_name'],
                    'bio': p_data['bio'],
                    'phone': p_data['phone'],
                    'is_verified': p_data['is_verified'],
                    'is_active': True
                }
            )
        
        # عملاء
        customers_data = [
            {'username': 'customer1', 'first_name': 'محمد', 'last_name': 'العميل'},
            {'username': 'customer2', 'first_name': 'زينب', 'last_name': 'العميلة'},
            {'username': 'customer3', 'first_name': 'عمر', 'last_name': 'الزبون'},
        ]
        
        for c_data in customers_data:
            user, created = User.objects.get_or_create(
                username=c_data['username'],
                defaults={
                    'email': f"{c_data['username']}@example.com",
                    'first_name': c_data['first_name'],
                    'last_name': c_data['last_name']
                }
            )
            if created:
                user.set_password('customer123')
                user.save()
                user.groups.add(Group.objects.get(name='Customer'))
        
        self.stdout.write(f'✓ تم إنشاء المستخدمين ومقدمي الخدمات')

    def create_categories(self):
        """إنشاء التصنيفات"""
        categories_data = [
            {'name': 'تصميم جرافيك', 'slug': 'graphic-design', 'icon': 'bi-palette', 'description': 'خدمات التصميم الجرافيكي والهوية البصرية', 'order': 1},
            {'name': 'تطوير ويب', 'slug': 'web-development', 'icon': 'bi-code-slash', 'description': 'تطوير المواقع والتطبيقات', 'order': 2},
            {'name': 'تسويق رقمي', 'slug': 'digital-marketing', 'icon': 'bi-megaphone', 'description': 'التسويق الإلكتروني وإدارة السوشيال ميديا', 'order': 3},
            {'name': 'تصوير', 'slug': 'photography', 'icon': 'bi-camera', 'description': 'التصوير الفوتوغرافي والفيديو', 'order': 4},
            {'name': 'كتابة محتوى', 'slug': 'content-writing', 'icon': 'bi-pencil', 'description': 'كتابة المحتوى والمقالات', 'order': 5},
            {'name': 'ترجمة', 'slug': 'translation', 'icon': 'bi-translate', 'description': 'خدمات الترجمة بجميع اللغات', 'order': 6},
            {'name': 'استشارات', 'slug': 'consulting', 'icon': 'bi-chat-dots', 'description': 'الاستشارات المهنية والأعمال', 'order': 7},
            {'name': 'تدريب', 'slug': 'training', 'icon': 'bi-mortarboard', 'description': 'الدورات التدريبية والتعليم', 'order': 8},
        ]
        
        for cat_data in categories_data:
            Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon'],
                    'description': cat_data['description'],
                    'order': cat_data['order'],
                    'is_active': True
                }
            )
        
        self.stdout.write(f'✓ تم إنشاء {len(categories_data)} تصنيف')

    def create_tags(self):
        """إنشاء الوسوم"""
        tags_data = [
            ('شعارات', 'logos'),
            ('مواقع', 'websites'),
            ('تطبيقات', 'apps'),
            ('سوشيال ميديا', 'social-media'),
            ('SEO', 'seo'),
            ('فيديو', 'video'),
            ('صور', 'photos'),
            ('محتوى', 'content'),
            ('إعلانات', 'ads'),
            ('هوية بصرية', 'branding'),
            ('UI/UX', 'ui-ux'),
            ('WordPress', 'wordpress'),
            ('Flutter', 'flutter'),
            ('Python', 'python'),
            ('React', 'react'),
        ]
        
        for tag_name, tag_slug in tags_data:
            Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': tag_slug}
            )
        
        self.stdout.write(f'✓ تم إنشاء {len(tags_data)} وسم')

    def create_services(self):
        """إنشاء الخدمات"""
        # جلب المقدمين والتصنيفات
        try:
            ahmed = Provider.objects.get(user__username='ahmed_designer')
            ali = Provider.objects.get(user__username='ali_developer')
            fatima = Provider.objects.get(user__username='fatima_marketing')
            hassan = Provider.objects.get(user__username='hassan_photo')
        except Provider.DoesNotExist:
            self.stdout.write(self.style.ERROR('خطأ: لم يتم العثور على مقدمي الخدمات'))
            return
        
        design_cat = Category.objects.get(slug='graphic-design')
        web_cat = Category.objects.get(slug='web-development')
        marketing_cat = Category.objects.get(slug='digital-marketing')
        photo_cat = Category.objects.get(slug='photography')
        
        services_data = [
            # خدمات أحمد - التصميم
            {
                'provider': ahmed,
                'category': design_cat,
                'title': 'تصميم شعار احترافي',
                'slug': 'professional-logo-design',
                'summary': 'تصميم شعار مميز وفريد يعبر عن هوية شركتك',
                'description': '''نقدم لك خدمة تصميم شعار احترافي يتضمن:
                
• 3 مقترحات تصميم أولية
• تعديلات غير محدودة حتى الوصول للتصميم المطلوب
• ملفات بجميع الصيغ (PNG, JPG, SVG, PDF, AI)
• دليل استخدام الشعار
• حقوق ملكية كاملة

مدة التنفيذ: 3-5 أيام عمل''',
                'price': 150000,
                'price_note': 'يبدأ من',
                'duration': '3-5 أيام',
                'is_featured': True,
                'tags': ['شعارات', 'هوية بصرية']
            },
            {
                'provider': ahmed,
                'category': design_cat,
                'title': 'تصميم هوية بصرية كاملة',
                'slug': 'complete-brand-identity',
                'summary': 'هوية بصرية متكاملة تشمل الشعار والألوان والخطوط',
                'description': '''باقة الهوية البصرية الكاملة تتضمن:

• تصميم الشعار
• اختيار الألوان والخطوط
• بطاقات العمل
• ورق رسمي
• توقيع البريد الإلكتروني
• دليل الهوية البصرية الكامل

استثمر في هوية بصرية قوية لعلامتك التجارية''',
                'price': 500000,
                'duration': '7-10 أيام',
                'is_featured': True,
                'tags': ['شعارات', 'هوية بصرية']
            },
            {
                'provider': ahmed,
                'category': design_cat,
                'title': 'تصميم منشورات سوشيال ميديا',
                'slug': 'social-media-posts-design',
                'summary': 'تصاميم جذابة لمنشورات السوشيال ميديا',
                'description': '''نصمم لك منشورات احترافية للسوشيال ميديا:

• 10 تصاميم شهرياً
• تنسيق لجميع المنصات (انستغرام، فيسبوك، تويتر)
• تصاميم متوافقة مع هوية علامتك
• ملفات قابلة للتعديل

حزمة شهرية لتعزيز تواجدك الرقمي''',
                'price': 100000,
                'price_note': 'شهرياً',
                'duration': 'مستمر',
                'is_featured': False,
                'tags': ['سوشيال ميديا', 'هوية بصرية']
            },
            
            # خدمات علي - البرمجة
            {
                'provider': ali,
                'category': web_cat,
                'title': 'تطوير موقع ويب متكامل',
                'slug': 'full-website-development',
                'summary': 'موقع ويب احترافي متجاوب مع جميع الأجهزة',
                'description': '''نطور لك موقع ويب متكامل يشمل:

• تصميم عصري ومتجاوب
• لوحة تحكم سهلة الاستخدام
• تحسين محركات البحث SEO
• شهادة SSL مجانية
• استضافة السنة الأولى مجاناً
• دعم فني لمدة 3 أشهر

تقنيات: Django, React, Bootstrap''',
                'price': 750000,
                'price_note': 'يبدأ من',
                'duration': '2-4 أسابيع',
                'is_featured': True,
                'tags': ['مواقع', 'Python', 'React']
            },
            {
                'provider': ali,
                'category': web_cat,
                'title': 'تطوير تطبيق موبايل',
                'slug': 'mobile-app-development',
                'summary': 'تطبيق موبايل لأندرويد وآيفون',
                'description': '''نطور لك تطبيق موبايل يعمل على:

• أندرويد وآيفون بكود موحد (Flutter)
• واجهة مستخدم جذابة وسهلة
• ربط مع APIs خارجية
• إشعارات فورية
• نشر على المتاجر (Google Play, App Store)
• دعم فني لمدة 6 أشهر

تقنيات: Flutter, Firebase''',
                'price': 1500000,
                'price_note': 'يبدأ من',
                'duration': '4-8 أسابيع',
                'is_featured': True,
                'tags': ['تطبيقات', 'Flutter']
            },
            {
                'provider': ali,
                'category': web_cat,
                'title': 'موقع WordPress مخصص',
                'slug': 'custom-wordpress-website',
                'summary': 'موقع WordPress احترافي مع قالب مخصص',
                'description': '''موقع WordPress متكامل:

• قالب مخصص حسب الطلب
• إضافات أساسية مهمة
• تدريب على إدارة الموقع
• تحسين السرعة والأداء
• نسخ احتياطية تلقائية

مناسب للشركات الصغيرة والمتوسطة''',
                'price': 300000,
                'duration': '1-2 أسبوع',
                'is_featured': False,
                'tags': ['مواقع', 'WordPress']
            },
            
            # خدمات فاطمة - التسويق
            {
                'provider': fatima,
                'category': marketing_cat,
                'title': 'إدارة حسابات سوشيال ميديا',
                'slug': 'social-media-management',
                'summary': 'إدارة احترافية لحساباتك على مواقع التواصل',
                'description': '''باقة إدارة السوشيال ميديا الشهرية:

• إدارة 3 منصات (انستغرام، فيسبوك، تويتر)
• 20 منشور شهرياً
• تصميم المحتوى البصري
• الرد على التعليقات والرسائل
• تقرير أداء شهري
• استراتيجية محتوى

نساعدك على بناء حضور رقمي قوي''',
                'price': 300000,
                'price_note': 'شهرياً',
                'duration': 'مستمر',
                'is_featured': True,
                'tags': ['سوشيال ميديا', 'محتوى']
            },
            {
                'provider': fatima,
                'category': marketing_cat,
                'title': 'حملة إعلانية على فيسبوك',
                'slug': 'facebook-ads-campaign',
                'summary': 'حملة إعلانية مدروسة على فيسبوك وانستغرام',
                'description': '''حملة إعلانية احترافية تشمل:

• دراسة السوق والجمهور المستهدف
• إعداد الحملة الإعلانية
• تصميم الإعلانات
• إدارة وتحسين الحملة لمدة شهر
• تقارير أداء أسبوعية
• تحسين مستمر للنتائج

*لا تشمل ميزانية الإعلانات''',
                'price': 200000,
                'duration': 'شهر واحد',
                'is_featured': False,
                'tags': ['إعلانات', 'سوشيال ميديا']
            },
            {
                'provider': fatima,
                'category': marketing_cat,
                'title': 'تحسين محركات البحث SEO',
                'slug': 'seo-optimization',
                'summary': 'تحسين ظهور موقعك في نتائج جوجل',
                'description': '''خدمة SEO شاملة:

• تحليل الموقع الحالي
• بحث الكلمات المفتاحية
• تحسين المحتوى
• SEO التقني
• بناء الروابط الخلفية
• تقارير شهرية

نتائج ملموسة خلال 3-6 أشهر''',
                'price': 250000,
                'price_note': 'شهرياً',
                'duration': '3-6 أشهر',
                'is_featured': False,
                'tags': ['SEO', 'مواقع']
            },
            
            # خدمات حسن - التصوير
            {
                'provider': hassan,
                'category': photo_cat,
                'title': 'تصوير منتجات احترافي',
                'slug': 'product-photography',
                'summary': 'تصوير منتجاتك بجودة عالية للمتاجر الإلكترونية',
                'description': '''تصوير منتجات احترافي:

• تصوير حتى 20 منتج
• خلفية بيضاء أو ملونة
• معالجة وتنقية الصور
• صور عالية الدقة
• ملفات جاهزة للطباعة والويب

مثالي للمتاجر الإلكترونية''',
                'price': 100000,
                'duration': '1-2 يوم',
                'is_featured': False,
                'tags': ['صور', 'محتوى']
            },
            {
                'provider': hassan,
                'category': photo_cat,
                'title': 'تصوير فيديو ترويجي',
                'slug': 'promotional-video',
                'summary': 'فيديو ترويجي قصير لشركتك أو منتجك',
                'description': '''فيديو ترويجي احترافي:

• فيديو مدته 30-60 ثانية
• سيناريو وتخطيط
• تصوير بكاميرات احترافية
• مونتاج وتأثيرات
• موسيقى مرخصة
• صيغ متعددة

يعزز تواجدك الرقمي ويجذب العملاء''',
                'price': 350000,
                'duration': '3-5 أيام',
                'is_featured': False,
                'tags': ['فيديو', 'محتوى']
            },
        ]
        
        for s_data in services_data:
            service, created = Service.objects.get_or_create(
                slug=s_data['slug'],
                defaults={
                    'provider': s_data['provider'],
                    'category': s_data['category'],
                    'title': s_data['title'],
                    'summary': s_data['summary'],
                    'description': s_data['description'],
                    'price': s_data['price'],
                    'price_note': s_data.get('price_note', ''),
                    'duration': s_data.get('duration', ''),
                    'is_active': True,
                    'is_featured': s_data.get('is_featured', False)
                }
            )
            
            if created:
                # إضافة الوسوم
                for tag_name in s_data.get('tags', []):
                    try:
                        tag = Tag.objects.get(name=tag_name)
                        service.tags.add(tag)
                    except Tag.DoesNotExist:
                        pass
        
        self.stdout.write(f'✓ تم إنشاء {len(services_data)} خدمة')

    def create_requests(self):
        """إنشاء طلبات تجريبية"""
        try:
            customer1 = User.objects.get(username='customer1')
            customer2 = User.objects.get(username='customer2')
            
            service1 = Service.objects.get(slug='professional-logo-design')
            service2 = Service.objects.get(slug='full-website-development')
            service3 = Service.objects.get(slug='social-media-management')
        except (User.DoesNotExist, Service.DoesNotExist):
            self.stdout.write(self.style.WARNING('تخطي إنشاء الطلبات - بيانات غير مكتملة'))
            return
        
        requests_data = [
            {
                'service': service1,
                'customer': customer1,
                'status': 'done',
                'customer_notes': 'أحتاج شعار لمطعم عراقي تراثي',
                'contact_phone': '07801234567'
            },
            {
                'service': service2,
                'customer': customer1,
                'status': 'in_progress',
                'customer_notes': 'موقع لشركة مقاولات مع معرض أعمال',
                'contact_phone': '07801234567'
            },
            {
                'service': service3,
                'customer': customer2,
                'status': 'approved',
                'customer_notes': 'إدارة حسابات محل ملابس نسائية',
                'contact_phone': '07802345678'
            },
            {
                'service': service1,
                'customer': customer2,
                'status': 'new',
                'customer_notes': 'شعار لصالون تجميل',
                'contact_phone': '07802345678'
            },
        ]
        
        for r_data in requests_data:
            ServiceRequest.objects.get_or_create(
                service=r_data['service'],
                customer=r_data['customer'],
                defaults={
                    'status': r_data['status'],
                    'customer_notes': r_data['customer_notes'],
                    'contact_phone': r_data['contact_phone']
                }
            )
        
        self.stdout.write(f'✓ تم إنشاء {len(requests_data)} طلب تجريبي')
