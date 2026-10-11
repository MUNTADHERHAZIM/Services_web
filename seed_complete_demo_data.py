"""
Complete Demo Data & Accounts Seeder for Ail Services Platform
بذر البيانات التجريبية الشاملة والحسابات المتكاملة
"""
import os
import django
from decimal import Decimal
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Provider, UserProfile, ProviderAgreement
from services.models import Category, Service, Tag, Review, ServicePackage, ServiceFeature, ServiceFAQ
from requests.models import ServiceRequest
from wallet.models import Wallet, Transaction
from conversations.models import Conversation, Message
from favorites.models import FavoriteService

print("🚀 Starting Complete Demo Data & Accounts Seeding...")

DEMO_PASSWORD = "Demo123456!"

# ============================================================================
# 1. Accounts: Providers & Customers
# ============================================================================

PROVIDERS_DATA = [
    {
        "username": "sajjad_electric",
        "first_name": "سجاد",
        "last_name": "الكهربائي",
        "email": "sajjad.electric@example.com",
        "title": "فني تمديدات وصيانة كهربائية عامة وذكية",
        "bio": "خبرة أكثر من 10 سنوات في صيانة وتأسيس شبكات الكهرباء المنزلية والصناعية وموازنة الأحمال وأنظمة الطاقة الشمسية في البصرة.",
        "phone": "+9647701122334",
        "city": "البصرة",
        "district": "المعقل",
        "address": "شارع الجمهورية - قرب تقاطع البهو",
        "level": Provider.Level.TOP_RATED,
        "hourly_rate": Decimal("25000.00"),
        "response_time": "خلال 30 دقيقة",
        "skills": ["تأسيس كهرباء", "إنارة ذكية", "لوحات توزيع", "طاقة شمسية", "صيانة سبلت"],
        "languages": ["العربية", "الإنجليزية"],
        "total_orders": 85,
        "completed_orders": 82,
        "gender": UserProfile.Gender.MALE,
    },
    {
        "username": "hassan_plumber",
        "first_name": "حسن",
        "last_name": "الصحيات",
        "email": "hassan.plumber@example.com",
        "title": "معلم تأسيسات صحية وكشف تسربات المياه",
        "bio": "متخصص في تأسيس شبكات المياه والمجاري، صيانة السخانات والمضخات وفلاتر المياه بأحدث الأجهزة الإلكترونية دون تكسير.",
        "phone": "+9647802233445",
        "city": "بغداد",
        "district": "المنصور",
        "address": "شارع 14 رمضان - مقابل مجمع الأميرات",
        "level": Provider.Level.LEVEL_THREE,
        "hourly_rate": Decimal("20000.00"),
        "response_time": "خلال ساعة",
        "skills": ["كشف تسربات", "تأسيس حمامات", "مضخات مياه", "تسليك مجاري", "سخانات شمسية"],
        "languages": ["العربية"],
        "total_orders": 64,
        "completed_orders": 61,
        "gender": UserProfile.Gender.MALE,
    },
    {
        "username": "zainab_design",
        "first_name": "زينب",
        "last_name": "الرسام",
        "email": "zainab.design@example.com",
        "title": "مصممة هوية بصرية وعلامات تجارية وواجهات مستخدم",
        "bio": "مصممة جرافيك و UI/UX محترفة بخبرة 6 سنوات، قمت بتنفيذ أكثر من 120 هوية بصرية لشركات ومشاريع ناشئة في العراق والخليج.",
        "phone": "+9647713344556",
        "city": "أربيل",
        "district": "عينكاوة",
        "address": "شارع كوران - بناية الأعمال الحديثة",
        "level": Provider.Level.TOP_RATED,
        "hourly_rate": Decimal("35.00"),
        "response_time": "خلال ساعتين",
        "skills": ["تصميم شعارات", "هوية بصرية", "UI/UX", "Adobe Illustrator", "Figma"],
        "languages": ["العربية", "الكردية", "الإنجليزية"],
        "total_orders": 128,
        "completed_orders": 125,
        "gender": UserProfile.Gender.FEMALE,
    },
    {
        "username": "ahmed_tech",
        "first_name": "أحمد",
        "last_name": "التكنولوجي",
        "email": "ahmed.tech@example.com",
        "title": "مهندس برمجيات وتطوير متاجر وتطبيقات سحابية",
        "bio": "مهندس برمجيات متفرغ متخصص في تطوير المواقع السريعة، متاجر الدفع الإلكتروني (زين كاش وماستركارد)، وتطبيقات Flutter المتجاوبة.",
        "phone": "+9647724455667",
        "city": "بغداد",
        "district": "الكرادة",
        "address": "شارع العرصات - مجمع البرمجيات",
        "level": Provider.Level.TOP_RATED,
        "hourly_rate": Decimal("40.00"),
        "response_time": "خلال 15 دقيقة",
        "skills": ["Django", "Python", "Flutter", "بوابات الدفع", "متاجر إلكترونية", "DevOps"],
        "languages": ["العربية", "الإنجليزية"],
        "total_orders": 92,
        "completed_orders": 90,
        "gender": UserProfile.Gender.MALE,
    },
    {
        "username": "karar_cars",
        "first_name": "كرار",
        "last_name": "المهندس",
        "email": "karar.cars@example.com",
        "title": "خبير فحص وبرمجة كمبيوتر وميكانيك سيارات متنقل",
        "bio": "خدمات فحص كمبيوتر دقيق، مسح أعطال، كشف شامل قبل الشراء مع ورشة متنقلة ومعدات فحص متطورة تصلك لباب بيتك.",
        "phone": "+9647815566778",
        "city": "البصرة",
        "district": "الجبيلة",
        "address": "الشارع التجاري العام",
        "level": Provider.Level.LEVEL_TWO,
        "hourly_rate": Decimal("30000.00"),
        "response_time": "خلال 45 دقيقة",
        "skills": ["فحص كمبيوتر OBD2", "برمجة حساسات", "كهرباء سيارات", "فحص قبل الشراء", "تعديل إلكتروني"],
        "languages": ["العربية"],
        "total_orders": 45,
        "completed_orders": 43,
        "gender": UserProfile.Gender.MALE,
    },
    {
        "username": "maryam_clean",
        "first_name": "مريم",
        "last_name": "البياتي",
        "email": "maryam.clean@example.com",
        "title": "إدارة فرق تنظيف منازل وشقق وتعقيم متكامل",
        "bio": "إشراف ومتابعة خدمات التنظيف العميق للفلل والبيوت والشقق، تنظيف واجهات، غسيل كنب ومفروشات بأجهزة البخار الحديثة ومواد صديقة للبيئة.",
        "phone": "+9647736677889",
        "city": "النجف",
        "district": "حي الغدير",
        "address": "شارع المدينة الرئيسي",
        "level": Provider.Level.LEVEL_TWO,
        "hourly_rate": Decimal("25000.00"),
        "response_time": "خلال ساعة",
        "skills": ["تنظيف عميق", "غسيل بخار", "تعقيم منازل", "تنظيف واجهات زجاج", "جلي كاشي ورخام"],
        "languages": ["العربية"],
        "total_orders": 58,
        "completed_orders": 56,
        "gender": UserProfile.Gender.FEMALE,
    }
]

CUSTOMERS_DATA = [
    {
        "username": "ali_client",
        "first_name": "علي",
        "last_name": "الكرخي",
        "email": "ali.client@example.com",
        "phone": "+9647708899001",
        "city": "بغداد",
        "district": "الكرخ",
        "address": "منطقة اليرموك - محلة 612",
        "gender": UserProfile.Gender.MALE,
    },
    {
        "username": "fatima_client",
        "first_name": "فاطمة",
        "last_name": "الزهراء",
        "email": "fatima.client@example.com",
        "phone": "+9647809900112",
        "city": "البصرة",
        "district": "الجزائر",
        "address": "شارع الوفود - قرب مستشفى الموسوي",
        "gender": UserProfile.Gender.FEMALE,
    },
    {
        "username": "omar_client",
        "first_name": "عمر",
        "last_name": "النعيمي",
        "email": "omar.client@example.com",
        "phone": "+9647710011223",
        "city": "أربيل",
        "district": "بختياري",
        "address": "مجمع بختياري السكني",
        "gender": UserProfile.Gender.MALE,
    }
]

created_providers = {}
created_customers = {}

# Seed Providers
for p_data in PROVIDERS_DATA:
    u, created = User.objects.get_or_create(username=p_data['username'], defaults={
        'email': p_data['email'],
        'first_name': p_data['first_name'],
        'last_name': p_data['last_name'],
        'is_active': True,
    })
    u.set_password(DEMO_PASSWORD)
    u.save()

    # User Profile
    up, _ = UserProfile.objects.get_or_create(user=u)
    up.user_type = UserProfile.UserType.PROVIDER
    up.phone_number = p_data['phone']
    up.city = p_data['city']
    up.district = p_data['district']
    up.address = p_data['address']
    up.gender = p_data['gender']
    up.id_type = UserProfile.IDType.NATIONAL_ID
    up.id_number = f"1990{u.id:06d}"
    up.id_verified = True
    up.verification_status = UserProfile.VerificationStatus.VERIFIED
    up.verified_at = timezone.now()
    up.provider_approved = True
    up.provider_approved_at = timezone.now()
    up.profile_completed = True
    up.completion_percentage = 100
    up.save()

    # Provider Profile
    prov, _ = Provider.objects.get_or_create(user=u, defaults={
        'display_name': f"{p_data['first_name']} {p_data['last_name']}",
    })
    prov.display_name = f"{p_data['first_name']} {p_data['last_name']}"
    prov.title = p_data['title']
    prov.bio = p_data['bio']
    prov.phone = p_data['phone']
    prov.level = p_data['level']
    prov.hourly_rate = p_data['hourly_rate']
    prov.response_time = p_data['response_time']
    prov.skills = p_data['skills']
    prov.languages = p_data['languages']
    prov.total_orders = p_data['total_orders']
    prov.completed_orders = p_data['completed_orders']
    prov.is_verified = True
    prov.is_active = True
    prov.save()

    # Provider Agreement
    pa, _ = ProviderAgreement.objects.get_or_create(provider=prov)
    pa.full_name = f"{p_data['first_name']} {p_data['last_name']}"
    pa.national_id = f"1990{u.id:06d}"
    pa.address = p_data['address']
    pa.phone_number = p_data['phone']
    pa.specialty = p_data['title']
    pa.conduct_agreement = True
    pa.professional_standards = True
    pa.commission_agreement = True
    pa.privacy_agreement = True
    pa.commission_percentage = Decimal("10.00")
    pa.save()

    # Wallet
    w, _ = Wallet.objects.get_or_create(user=u, defaults={
        'balance': Decimal("350000.00") if p_data['city'] != 'أربيل' else Decimal("280.00"),
        'currency': 'IQD' if p_data['city'] != 'أربيل' else 'USD',
        'total_earned': Decimal("1200000.00") if p_data['city'] != 'أربيل' else Decimal("950.00"),
        'is_active': True
    })

    created_providers[p_data['username']] = prov
    print(f"  ✅ Provider created/ready: {prov.display_name} (@{u.username})")

# Seed Customers
for c_data in CUSTOMERS_DATA:
    u, created = User.objects.get_or_create(username=c_data['username'], defaults={
        'email': c_data['email'],
        'first_name': c_data['first_name'],
        'last_name': c_data['last_name'],
        'is_active': True,
    })
    u.set_password(DEMO_PASSWORD)
    u.save()

    up, _ = UserProfile.objects.get_or_create(user=u)
    up.user_type = UserProfile.UserType.CUSTOMER
    up.phone_number = c_data['phone']
    up.city = c_data['city']
    up.district = c_data['district']
    up.address = c_data['address']
    up.gender = c_data['gender']
    up.id_verified = True
    up.verification_status = UserProfile.VerificationStatus.VERIFIED
    up.profile_completed = True
    up.completion_percentage = 95
    up.save()

    # Wallet for customer
    w, _ = Wallet.objects.get_or_create(user=u, defaults={
        'balance': Decimal("150000.00"),
        'currency': 'IQD',
        'is_active': True
    })

    created_customers[c_data['username']] = u
    print(f"  ✅ Customer created/ready: {u.get_full_name()} (@{u.username})")

# ============================================================================
# 2. Services Data Creation
# ============================================================================
print("\n📦 Seeding Services across categories...")

# Helper to find category
def get_cat(name_query):
    cat = Category.objects.filter(name__icontains=name_query).first()
    return cat or Category.objects.first()

services_catalog_data = [
    {
        "provider": created_providers["sajjad_electric"],
        "category": get_cat("كهرباء"),
        "title": "تأسيس وصيانة كهرباء المنازل والشركات وفحص اللوحات الذكية",
        "slug": "electrical-maintenance-smart-panels-basra",
        "summary": "خدمة صيانة كهربائية سريعة وشاملة لتصليح القواطع، تمديد خطوط المولد والشبكة، وموازنة الأحمال الكهربائية بكفاءة.",
        "description": "فني كهرباء معتمد بخبرة واسعة يقدم خدمات صيانة وإصلاح كافة الأعطال المنزلية والصناعية:\n- تمديد خطوط الكهرباء الداخلية والخارجية.\n- فحص التسريب الأرضي وتثبيت قواطع الحماية الذكية (Earth Leakage).\n- توزيع وموازنة الأحمال على خطوط السحب والمولد الوطني.\n- تركيب إنارة سبوت لايت، ليد مخفي، وأنظمة الإنارة الحديثة.\n- ضمان سلامة التمديدات لمدة 6 أشهر.",
        "price": Decimal("25000.00"),
        "original_price": Decimal("35000.00"),
        "currency": "IQD",
        "price_note": "أجور كشفية مع الصيانة الأولية",
        "duration": "نفس اليوم (1-3 ساعات)",
        "level": Service.Level.EXPERT,
        "is_featured": True,
        "is_active": True,
        "discount_end_date": timezone.now() + timedelta(days=20),
        "packages": [
            {"name": "كشف وإصلاح عطل مفرد", "type": ServicePackage.PackageType.BASIC, "price": Decimal("25000.00"), "days": 1, "desc": "فحص العطل الكهربائي الفوري وإصلاح نقطة أو قاطع واحد."},
            {"name": "صيانة دورية وموازنة أحمال المنزل", "type": ServicePackage.PackageType.STANDARD, "price": Decimal("60000.00"), "days": 1, "desc": "فحص اللوحة الرئيسية، شد المسامير المرتخية، قياس التيارات، وموازنة الأحمال بين الخطوط."},
            {"name": "تأسيس غرفة أو صالة متكاملة", "type": ServicePackage.PackageType.PREMIUM, "price": Decimal("140000.00"), "days": 3, "desc": "تمديد بايبات، أسلاك حرارية معتمدة، نقاط كهرباء وإنارة مخفية كاملة مع الضمان."},
        ],
        "features": [
            {"title": "حضور سريع وميداني", "desc": "الوصول لموقعك في أقل من ساعة من تأكيد الطلب.", "icon": "bi-lightning-charge-fill"},
            {"title": "أجهزة قياس رقمية", "desc": "استخدام أحدث أجهزة فحص العوازل والفولتية بدقة عالية.", "icon": "bi-speedometer2"},
            {"title": "ضمان جودة العمل", "desc": "ضمان مكتوب على أعمال الصيانة لمدة 6 أشهر كاملة.", "icon": "bi-shield-check"},
        ],
        "faqs": [
            {"q": "هل توفرون قطع الغيار والأسلاك؟", "a": "نعم، يمكننا توفير المواد الأصلية المعتمدة بأسعار الجملة، أو يمكن للعميل توفيرها إذا رغب."},
            {"q": "ما هي مناطق التغطية في البصرة؟", "a": "نغطي كافة أحياء مركز محافظة البصرة والزبير والهارثة وشط العرب."},
        ]
    },
    {
        "provider": created_providers["sajjad_electric"],
        "category": get_cat("تكييف"),
        "title": "غسيل وصيانة أجهزة التكييف والسبالت مع شحن فريون أصلي وكفالة",
        "slug": "ac-split-cleaning-repair-gas-refill",
        "summary": "غسيل وتنظيف عميق لوحدات التكييف الداخلية والخارجية بمضخات الضغط مع فحص التبريد والغاز الأمريكي الأصلي.",
        "description": "استعد لحرارة الصيف بأعلى كفاءة تبريد لجهازك مع التوفير باستهلاك الكهرباء:\n1. تنظيف عميق بدون فك الجهاز عبر كفرات حماية مخصصة ومضخات ماء مضغوط.\n2. تعقيم حوض التصريف والفلاتر بمواد مزيلة للبكتيريا والروائح الكريهة.\n3. قياس ضغط الغاز وتعبئة فريون أصلي معتمد (R22 أو R410A).\n4. فحص الأمبير والمكثف (الكابستر) واهتزازات المحرك.",
        "price": Decimal("30000.00"),
        "original_price": Decimal("45000.00"),
        "currency": "IQD",
        "price_note": "للجهاز الواحد (طن ونص - طنين)",
        "duration": "ساعتين",
        "level": Service.Level.EXPERT,
        "is_featured": True,
        "is_active": True,
        "discount_end_date": timezone.now() + timedelta(days=12),
        "packages": [
            {"name": "غسيل وتنظيف سبلت واحد", "type": ServicePackage.PackageType.BASIC, "price": Decimal("30000.00"), "days": 1, "desc": "غسيل القطعة الداخلية والخارجية وتنظيف الفلاتر ومجرى التصريف."},
            {"name": "غسيل سبلت مع تعبئة غاز فريون", "type": ServicePackage.PackageType.STANDARD, "price": Decimal("50000.00"), "days": 1, "desc": "غسيل كامل + شحن الغاز الأمريكي الناقص مع فحص التسريب."},
            {"name": "باقة الصيانة الشاملة (3 سبالت)", "type": ServicePackage.PackageType.PREMIUM, "price": Decimal("110000.00"), "days": 1, "desc": "غسيل شامل وفحص لثلاثة أجهزة تكييف بخصم خاص للعوائل."},
        ],
        "features": [
            {"title": "غسيل نظيف دون فوضى", "desc": "استخدام أغطية عازلة لحماية الجدران والأثاث من رذاذ الماء.", "icon": "bi-droplet-fill"},
            {"title": "غاز أصلي نقي 100%", "desc": "غاز تبريد عالي النقاوة يحمي ضاغط السبلت ويضمن برودة ممتازة.", "icon": "bi-snow"},
        ],
        "faqs": [
            {"q": "كم يستغرق تنظيف الجهاز الواحد؟", "a": "يستغرق تنظيف الجهاز قرابة 40 دقيقة شاملاً فحص التبريد وتصريف المياه."},
        ]
    },
    {
        "provider": created_providers["hassan_plumber"],
        "category": get_cat("سباكة"),
        "title": "كشف تسربات المياه إلكترونياً وصيانة وتأسيس الصحيات وتصليح السخانات",
        "slug": "leak-detection-plumbing-repairs-baghdad",
        "summary": "كشف دقيق لمكان كسر البايبات والتسربات بدون تكسير عشوائي مع صيانة خلاطات وسخانات وتركيب أطقم صحية.",
        "description": "حل نهائي لمشاكل الرطوبة وارتفاع فاتورة الماء وانسداد المجاري في بغداد:\n- كشف تسربات الأنابيب بأجهزة التحسس الصوتي والكاميرات الحرارية.\n- صيانة واستبدال مضخات المياه الإيطالية وتركيب أوتوماتيك الضغط.\n- تسليك المجاري بمكائن الضغط والزنبرك الكهربائي.\n- تأسيس وصيانة شبكات المياه الحرارية (PPR) وخزانات الأسطح مع الضمان.",
        "price": Decimal("35000.00"),
        "original_price": Decimal("50000.00"),
        "currency": "IQD",
        "price_note": "كشفية وفحص إلكتروني",
        "duration": "نفس اليوم",
        "level": Service.Level.PROFESSIONAL,
        "is_featured": True,
        "is_active": True,
        "discount_end_date": timezone.now() + timedelta(days=25),
        "packages": [
            {"name": "فحص وكشف تسرب نقطة واحدة", "type": ServicePackage.PackageType.BASIC, "price": Decimal("35000.00"), "days": 1, "desc": "كشف موقع الخلل بالأجهزة المتطورة مع تحديد مكان العطل بدقة."},
            {"name": "صيانة وتركيب طقم خلاطات ومغاسل", "type": ServicePackage.PackageType.STANDARD, "price": Decimal("75000.00"), "days": 1, "desc": "تركيب وصيانة مغاسل وخلاطات مياه ومرحاض وإصلاح العوامات."},
            {"name": "تسليك وترميم شبكة صحيات كاملة", "type": ServicePackage.PackageType.PREMIUM, "price": Decimal("180000.00"), "days": 2, "desc": "معالجة شاملة للانسدادات وتبديل بايبات التغذية التالفة."},
        ],
        "features": [
            {"title": "كشف بدون تكسير", "desc": "تحديد موضع التسريب بالسنتيمتر لتفادي تشويه البلاط والسيراميك.", "icon": "bi-search"},
            {"title": "معدات أوروبية متطورة", "desc": "أحدث مكائن كبس البايبات والتسليك السريع.", "icon": "bi-wrench-adjustable"},
        ],
        "faqs": [
            {"q": "هل تقدمون ضماناً بعد تصليح التسريب؟", "a": "نعم، نقدم ضماناً لمدة عام كامل على الوصلات والبايبات التي نقوم بتغييرها."},
        ]
    },
    {
        "provider": created_providers["zainab_design"],
        "category": get_cat("تصميم"),
        "title": "تصميم هوية بصرية كاملة وشعار احترافي فريد للشركات والمشاريع",
        "slug": "complete-branding-logo-design-package-pro",
        "summary": "باقة براندينغ متكاملة تشمل الشعار المبتكر، الخطوط، الألوان، المطبوعات، وقالب السوشيال ميديا بملفات مفتوحة المصدر.",
        "description": "امنح مشروعك هوية بصرية متميزة ترسخ في ذهن عملائك وتعكس فخامة علامتك التجارية:\n1. دراسة استراتيجية لعلامتك التجارية والمنافسين في السوق.\n2. تقديم 3 مفاهيم شعار مختلفة وأصلية 100% غير مكررة أو منسوخة.\n3. دليل الهوية البصرية (Brand Guidelines) يحتوي على معايير استخدام الشعار، الألوان، والخطوط.\n4. تصميم المطبوعات: كارت أعمال، فولدر، ورق رسمي، أظرف، وأكياس تسوق.\n5. قوالب سوشيال ميديا (Instagram & Facebook Post/Story).\n6. تسليم الملفات بصيغ: AI, PSD, SVG, PNG, PDF بدقة عالية جاهزة للطباعة.",
        "price": Decimal("95.00"),
        "original_price": Decimal("150.00"),
        "currency": "USD",
        "price_note": "شامل تعديلات غير محدودة حتى الرضا",
        "duration": "3-5 أيام عمل",
        "level": Service.Level.EXPERT,
        "is_featured": True,
        "is_active": True,
        "discount_end_date": timezone.now() + timedelta(days=15),
        "packages": [
            {"name": "باقة الشعار الأساسي", "type": ServicePackage.PackageType.BASIC, "price": Decimal("45.00"), "days": 3, "desc": "نموذجان للشعار + لوحة الألوان + ملفات PNG شفافة وPDF عالي الدقة."},
            {"name": "باقة الهوية الكاملة (الأكثر طلباً)", "type": ServicePackage.PackageType.STANDARD, "price": Decimal("95.00"), "days": 5, "desc": "3 نماذج شعار + ملف Brand Guide + كارت عمل وورق رسمي + الملفات المفتوحة AI."},
            {"name": "الباقة المؤسسية الشاملة", "type": ServicePackage.PackageType.PREMIUM, "price": Decimal("180.00"), "days": 7, "desc": "هوية بصرية شاملة + قوالب السوشيال ميديا + يونيفورم وسيارات + بروفايل الشركة التعريفي."},
        ],
        "features": [
            {"title": "أفكار إبداعية حصرية", "desc": "تصاميم مبتكرة صممت من الصفر خصيصاً لهوية مشروعك.", "icon": "bi-stars"},
            {"title": "ملفات فيكتور مفتوحة", "desc": "تسليم كافة ملفات المصدر Vector AI بجودة لا تتأثر بالتكبير.", "icon": "bi-file-earmark-code"},
            {"title": "تعديلات مرنة ومريحة", "desc": "متابعة مستمرة ومفتوحة حتى نصل للنتيجة التي تبهرك.", "icon": "bi-arrow-repeat"},
        ],
        "faqs": [
            {"q": "هل الشعار قابل للتسجيل كعلامة تجارية؟", "a": "نعم، كافة تصاميمنا أصلية 100% وخالية من أي حقوق ملكية فكرية مسبقة."},
        ]
    },
    {
        "provider": created_providers["ahmed_tech"],
        "category": get_cat("برمجة"),
        "title": "برمجة متجر إلكتروني احترافي يدعم بوابات الدفع العراقية وتتبع الشحنات",
        "slug": "custom-ecommerce-store-zaincash-delivery",
        "summary": "متجر إلكتروني عالي السرعة، لوحة تحكم عربية كاملة، دعم الدفع بـ زين كاش والماستركارد، وربط مباشر مع شركات التوصيل.",
        "description": "انقل تجارتك إلى الفضاء الرقمي مع متجر إلكتروني متكامل مصمم لزيادة المبيعات في السوق العراقي:\n- متجر فائق السرعة متوافق 100% مع الهواتف الذكية وتطبيق PWA.\n- ربط بوابات الدفع الإلكتروني (زين كاش ZainCash، FIB، آسيا حوالة، وماستركارد).\n- لوحة تحكم ذكية لإدارة المنتجات، المخزون، الطلبات، والخصومات والكوبونات.\n- حساب تكلفة التوصيل التلقائي لجميع محافظات العراق الـ 18.\n- إشعارات فورية عبر الواتساب للعميل عند تغيير حالة الطلب.\n- حماية وأمان عالي مع شهادة SSL واستضافة سحابية مجانية لأول سنة.",
        "price": Decimal("280.00"),
        "original_price": Decimal("400.00"),
        "currency": "USD",
        "price_note": "شامل الاستضافة والدومين والربط",
        "duration": "7-10 أيام عمل",
        "level": Service.Level.EXPERT,
        "is_featured": True,
        "is_active": True,
        "discount_end_date": timezone.now() + timedelta(days=18),
        "packages": [
            {"name": "متجر المنتجات الأساسي", "type": ServicePackage.PackageType.BASIC, "price": Decimal("190.00"), "days": 5, "desc": "متجر حتى 50 منتج + دفع عند الاستلام + لوحة تحكم سهلة."},
            {"name": "المتجر الاحترافي (شامل الدفع الإلكتروني)", "type": ServicePackage.PackageType.STANDARD, "price": Decimal("280.00"), "days": 8, "desc": "منتجات غير محدودة + ربط زين كاش وماستركارد + إشعارات واتساب وتتبع الشحن."},
            {"name": "المنصة التجارية المتكاملة + تطبيق", "type": ServicePackage.PackageType.PREMIUM, "price": Decimal("520.00"), "days": 15, "desc": "متجر ويب + تطبيق هاتف PWA + نظام نقاط البيع POS وربط محاسبي."},
        ],
        "features": [
            {"title": "بوابات دفع عراقية جاهزة", "desc": "ربط رسمي ومعتمد مع زين كاش ومصرف الرافدين والتجارة وغيرها.", "icon": "bi-credit-card-2-front-fill"},
            {"title": "سرعة تحميل خيالية", "desc": "أداء عالي على شبكات 4G و 3G مع تقنيات التخزين المؤقت المتقدمة.", "icon": "bi-rocket-takeoff-fill"},
            {"title": "دعم فني وتدريب", "desc": "فيديوهات تدريبية لك ولفريقك مع دعم فني مستمر لمدة 3 أشهر.", "icon": "bi-headset"},
        ],
        "faqs": [
            {"q": "هل أحتاج لخبرة برمجية لإدارة المتجر؟", "a": "إطلاقاً، لوحة التحكم مصممة باللغة العربية وهي سهلة جداً مثل استخدام تطبيقات الهاتف."},
        ]
    },
    {
        "provider": created_providers["karar_cars"],
        "category": get_cat("سيارات"),
        "title": "فحص كمبيوتر سيارات متنقل وبرمجة مفاتيح وحساسات وكشف ما قبل الشراء",
        "slug": "mobile-car-computer-diagnostics-basra",
        "summary": "فحص متنقل يصلك لمكان سيارتك أو المعرض، كشف الأعطال بالكمبيوتر المحدث، وفحص الشاصي والمحرك والصبغ.",
        "description": "لا تشتري سيارة مستعملة وتندم! نوفر لك فحصاً تقنياً شاملاً قبل اتخاذ القرار:\n1. كشف كمبيوتر كامل للمحرك، ناقل الحركة (الجير)، الوسائد الهوائية، وABS.\n2. قياس سماكة الصبغ بجهاز إلكتروني لكشف الحوادث والسمكرة والرش التجميلي.\n3. قراءة البيانات الحية لحساسات الأوكسجين والحرارة والاحتراق وضغط الوقود.\n4. مسح أكواد الأعطال (Check Engine) وإعادة ضبط الإعدادات المصنعية.\n5. تسليم تقرير فحص تفصيلي مطبوع وفوري يوضح حالة السيارة بدقة.",
        "price": Decimal("35000.00"),
        "original_price": Decimal("50000.00"),
        "currency": "IQD",
        "price_note": "شامل فحص المحرك والصبغ والكمبيوتر",
        "duration": "ساعة واحدة",
        "level": Service.Level.PROFESSIONAL,
        "is_featured": True,
        "is_active": True,
        "discount_end_date": timezone.now() + timedelta(days=30),
        "packages": [
            {"name": "فحص كمبيوتر ومسح أكواد فقط", "type": ServicePackage.PackageType.BASIC, "price": Decimal("20000.00"), "days": 1, "desc": "تشخيص الأعطال بالكمبيوتر وتحديد القطع المتعطلة ومسح الأكواد."},
            {"name": "فحص ما قبل الشراء الشامل", "type": ServicePackage.PackageType.STANDARD, "price": Decimal("35000.00"), "days": 1, "desc": "فحص كمبيوتر + فحص صبغ وبدي + فحص شاصي ومحرك مع تقرير مكتوب."},
            {"name": "فحص برمجي مع ضبط الحساسات وبرمجة دعسة", "type": ServicePackage.PackageType.PREMIUM, "price": Decimal("65000.00"), "days": 1, "desc": "برمجة الحساسات وسرعة الخمول ومطابقة المفاتيح وضبط الكمبيوتر."},
        ],
        "features": [
            {"title": "ورشة متنقلة تصلك أينما كنت", "desc": "نأتي إليك في بيتك أو في معارض السيارات بالبصرة.", "icon": "bi-geo-alt-fill"},
            {"title": "أجهزة أصلية معتمدة", "desc": "نستخدم أحدث أجهزة Launch و Autel الداعمة لكافة موديلات السيارات الحديثة.", "icon": "bi-cpu-fill"},
        ],
        "faqs": [
            {"q": "هل تفحصون سيارات الهايبرد والكهربائية؟", "a": "نعم، ندعم سيارات البنزين، الديزل، والهايبرد الشائعة مثل تويوتا وهيونداي وكيا."},
        ]
    },
    {
        "provider": created_providers["maryam_clean"],
        "category": get_cat("تنظيف"),
        "title": "تنظيف وتعقيم عميق للمنازل والفلل وغسيل الكنب والمفروشات بالبخار",
        "slug": "deep-home-cleaning-carpet-furniture-steam",
        "summary": "طاقم مدرب ومجهز بأحدث معدات الشفط والبخار لتنظيف الأرضيات، المطابخ، الحمامات، وغسيل الأطقم والسجاد بأعلى جودة.",
        "description": "اجعل منزلك يشع نظافة وانتعاشاً مع خدمة التنظيف الاحترافي المتكامل:\n- جلي وتلميع أرضيات السيراميك والبورسلين والرخام بمكائن متخصصة.\n- غسيل الكنب، المجالس العربية، والستائر بالبخار الحار لإزالة أصعب البقع والروائح والجراثيم.\n- إزالة دهون المطابخ المستعصية وتنظيف الأفران والشفاطات بعمق.\n- تنظيف وتعقيم أطقم الحمامات والمرايا والزجاج بمواد معتمدة وآمنة للأطفال.",
        "price": Decimal("75000.00"),
        "original_price": Decimal("100000.00"),
        "currency": "IQD",
        "price_note": "شقة متوسطة أو غسيل طقم مجلس",
        "duration": "نصف يوم عمل",
        "level": Service.Level.PROFESSIONAL,
        "is_featured": True,
        "is_active": True,
        "discount_end_date": timezone.now() + timedelta(days=14),
        "packages": [
            {"name": "غسيل طقم كنب أو مجلس", "type": ServicePackage.PackageType.BASIC, "price": Decimal("40000.00"), "days": 1, "desc": "غسيل بخار عميق وتعطير لطقم كنب حتى 7 مقاعد."},
            {"name": "تنظيف شقة سكنية متكاملة", "type": ServicePackage.PackageType.STANDARD, "price": Decimal("75000.00"), "days": 1, "desc": "تنظيف الأرضيات والشبابيك والمطبخ والحمامات لشقة تصل لـ 150م2."},
            {"name": "تنظيف فيلا أو منزل كبير بعد التشطيب", "type": ServicePackage.PackageType.PREMIUM, "price": Decimal("180000.00"), "days": 1, "desc": "إزالة بقايا الصبغ والترميمات وجلي الأرضيات وتعقيم البيت بالكامل مع فريق كامل."},
        ],
        "features": [
            {"title": "مواد ألمانية آمنة", "desc": "منظفات ومعقمات معتمدة لا تترك روائح خانقة ولا تضر بالأقمشة.", "icon": "bi-shield-shaded"},
            {"title": "أجهزة بخار إيطالية", "desc": "قوة بخار حراري تقضي على 99% من البكتيريا وتجفف سريعاً.", "icon": "bi-stars"},
        ],
        "faqs": [
            {"q": "كم يستغرق جفاف الكنب بعد الغسيل بالبخار؟", "a": "بفضل تقنية الشفط القوي، يجف الكنب تماماً خلال 2-3 ساعات فقط."},
        ]
    }
]

created_services = []

for s_data in services_catalog_data:
    svc, created = Service.objects.update_or_create(
        slug=s_data['slug'],
        defaults={
            'provider': s_data['provider'],
            'category': s_data['category'],
            'title': s_data['title'],
            'summary': s_data['summary'],
            'description': s_data['description'],
            'price': s_data['price'],
            'original_price': s_data['original_price'],
            'currency': s_data['currency'],
            'price_note': s_data['price_note'],
            'duration': s_data['duration'],
            'level': s_data['level'],
            'is_featured': s_data['is_featured'],
            'is_active': s_data['is_active'],
            'discount_end_date': s_data.get('discount_end_date'),
            'views_count': 120,
            'orders_count': 18,
            'avg_rating': Decimal("4.9"),
            'total_reviews': 6,
        }
    )
    created_services.append(svc)

    # Packages
    for idx, pkg in enumerate(s_data.get('packages', [])):
        ServicePackage.objects.update_or_create(
            service=svc,
            name=pkg['name'],
            defaults={
                'package_type': pkg['type'],
                'price': pkg['price'],
                'duration_days': pkg['days'],
                'description': pkg['desc'],
                'order': idx,
                'is_active': True,
            }
        )

    # Features
    for idx, feat in enumerate(s_data.get('features', [])):
        ServiceFeature.objects.update_or_create(
            service=svc,
            title=feat['title'],
            defaults={
                'description': feat['desc'],
                'icon': feat['icon'],
                'order': idx,
            }
        )

    # FAQs
    for idx, faq in enumerate(s_data.get('faqs', [])):
        ServiceFAQ.objects.update_or_create(
            service=svc,
            question=faq['q'],
            defaults={
                'answer': faq['a'],
                'order': idx,
                'is_active': True,
            }
        )

    print(f"  ⭐ Service ready: {svc.title[:40]}... ({svc.get_primary_price_display()})")

# ============================================================================
# 3. Reviews & Ratings
# ============================================================================
print("\n🌟 Seeding Realistic Reviews & Ratings...")

REVIEWS_SEED = [
    {
        "service_slug": "electrical-maintenance-smart-panels-basra",
        "customer": created_customers["fatima_client"],
        "rating": 5,
        "title": "شغل نظيف جداً والتزام عالي بالوقت",
        "comment": "الأخ سجاد إنسان محترم جداً وفاهم بشغله. حضر خلال نصف ساعة فقط وقام بفحص قواطع البيت وموازنة خطوط السحب وحل مشكلة الشورت اللي كانت تطفي السبلت. الله يبارك برزقه.",
        "pros": "سرعة الحضور، الالتزام بالأسعار المحددة، والنظافة في العمل",
        "cons": "لا يوجد، الخدمة كانت ممتازة",
        "response": "شكراً جزيلاً أختي الكريمة، بخدمتكم دائماً وهذا واجبنا للحفاظ على سلامة بيوتكم.",
    },
    {
        "service_slug": "electrical-maintenance-smart-panels-basra",
        "customer": created_customers["ali_client"],
        "rating": 5,
        "title": "فني محترف وأمين ومعدات حديثة",
        "comment": "قام بتمديد أسلاك الإنارة المخفية والسبوت لايت في الصالة بشكل هندسي جميل جداً واستخدم بايبات عازلة ممتازة. أنصح بالتعامل معه بشدة.",
        "pros": "دقة في المواعيد وخبرة بالإنارة الديكورية الحديثة",
        "cons": "لا يوجد",
        "response": "أهلاً بك أخي علي العزيز، سعدت بالعمل معك ومبارك منزلك الجديد.",
    },
    {
        "service_slug": "ac-split-cleaning-repair-gas-refill",
        "customer": created_customers["fatima_client"],
        "rating": 5,
        "title": "السبلت رجع ثلاجة وغسيل بدون أي قطرة مي عالأثاث",
        "comment": "استخدموا كفر خاص للتنظيف وغسلوا الوحدة الخارجية والداخلية بضغط عالي وفحصوا الغاز، التبريد اختلف 180 درجة وصوت المروحة صار هادئ جداً.",
        "pros": "نظافة فائقة، عدم إحداث فوضى، وغاز أمريكي أصلي",
        "cons": "تمنيت لو بدأوا قبل موعد الظهيرة فقط لشدة الحرارة",
        "response": "بالعافية عليكم، وسنراعي وقت الزيارة مبكراً في المرات القادمة إن شاء الله.",
    },
    {
        "service_slug": "leak-detection-plumbing-repairs-baghdad",
        "customer": created_customers["ali_client"],
        "rating": 5,
        "title": "كشف التسريب بالجهاز بدون تكسير الحمام كله",
        "comment": "كان عندي رطوبة دمرت صبغ الغرفة، الأستاذ حسن طلع التسريب بجهاز الصوت وكسر كاشية واحدة فقط وصلح البايب المكسور وصبغ وراه. وفر علي ملايين الدنانير.",
        "pros": "توفير التكاليف، أجهزة فحص حديثة، وقطع غيار إيطالية",
        "cons": "لا شيء يذكر",
        "response": "شكراً لثقتكم بنا أستاذ علي، هدفنا دوماً المحافظة على ممتلكاتكم بأقل ضرر.",
    },
    {
        "service_slug": "complete-branding-logo-design-package-pro",
        "customer": created_customers["omar_client"],
        "rating": 5,
        "title": "ذوق رفيع وهوية بصرية فخمة جداً",
        "comment": "الأخت زينب مبدعة حقيقية، صممت لشركتنا في أربيل هوية بصرية وشعار نال إعجاب كل الشركاء والعملاء. صبورة بالتعديلات وسلمتنا جميع الملفات بجودة خيالية.",
        "pros": "فهم عميق للهوية التجارية، التزام بوقت التسليم، وتسليم ملفات الـ AI كاملة",
        "cons": "لا يوجد",
        "response": "سعدت جداً بالتعاون معكم أستاذ عمر وأتمنى لمشروعكم كل التوفيق والنجاح!",
    },
    {
        "service_slug": "custom-ecommerce-store-zaincash-delivery",
        "customer": created_customers["omar_client"],
        "rating": 5,
        "title": "متجر سريع جداً وربط زين كاش اشتغل من أول يوم",
        "comment": "المهندس أحمد مبرمج من الطراز الأول، عمل لنا متجراً إلكترونياً سريعاً، صمم نظام الفواتير وربط زين كاش وتتبع الشحنات مع شركة التوصيل بكل سلاسة، مع تدريب الموظفين.",
        "pros": "سرعة الرد، أمان عالي للكود، وتوافق تام مع الجوال",
        "cons": "لا يوجد",
        "response": "تحياتي أخي عمر، هذا واجبي والمتجر جاهز لمواكبة آلاف الطلبات اليومية.",
    },
    {
        "service_slug": "mobile-car-computer-diagnostics-basra",
        "customer": created_customers["fatima_client"],
        "rating": 5,
        "title": "فحص سيارة دقيق قبل الشراء وأنقذني من سيارة مقلوبة",
        "comment": "طلبت خدمة فحص قبل الشراء في معارض البصرة، الأستاذ كرار كشف بجهاز الصبغ إن السقف والأبواب مرشوشة والشاصي فيه لحيم والكمبيوتر ماسحين أخطاء الجير. فحص أمين ومحترف جداً.",
        "pros": "أمانة عالية وتقرير مطبوع يفصل كل برغي في السيارة",
        "cons": "لا شيء",
        "response": "أمانة المهنة هي الأهم، وسلامتكم ورضاكم هو غايتنا دوماً.",
    },
    {
        "service_slug": "deep-home-cleaning-carpet-furniture-steam",
        "customer": created_customers["ali_client"],
        "rating": 5,
        "title": "تنظيف احترافي وتعقيم رائع بعد التشطيب",
        "comment": "الفريق بقيادة الأخت مريم أنجز تنظيف الفيلا بالكامل وإزالة آثار الصبغ والإسمنت والكنب عاد كالجديد برائحة عطرة جداً. التزام ممتاز بالوقت.",
        "pros": "فريق منظم، أجهزة بخار قوية، وسرعة في الإنجاز",
        "cons": "لا يوجد",
        "response": "شكراً جزيلاً لتقييمك الراقي، نتشرف بخدمتكم في أي وقت.",
    }
]

for r_data in REVIEWS_SEED:
    try:
        svc = Service.objects.get(slug=r_data["service_slug"])
        rev, created = Review.objects.update_or_create(
            service=svc,
            customer=r_data["customer"],
            defaults={
                "rating": r_data["rating"],
                "title": r_data["title"],
                "comment": r_data["comment"],
                "pros": r_data.get("pros", ""),
                "cons": r_data.get("cons", ""),
                "is_verified_purchase": True,
                "helpful_count": 8,
                "provider_response": r_data.get("response", ""),
                "provider_response_date": timezone.now() - timedelta(days=2),
                "is_approved": True,
            }
        )
        # Update Service rating
        svc.avg_rating = Decimal("4.9")
        svc.total_reviews = svc.reviews.count()
        svc.save(update_fields=['avg_rating', 'total_reviews'])
        print(f"  ⭐ Review seeded on [{svc.title[:25]}...] by @{r_data['customer'].username}")
    except Service.DoesNotExist:
        pass

# ============================================================================
# 4. Service Requests (Orders)
# ============================================================================
print("\n📋 Seeding Service Requests (Orders)...")

REQUESTS_SEED = [
    {
        "service_slug": "electrical-maintenance-smart-panels-basra",
        "customer": created_customers["fatima_client"],
        "status": ServiceRequest.Status.DONE,
        "notes": "أريد فحص لوحة القواطع الرئيسية وتصليح قاطع السبلت في غرفة النوم بالبصرة.",
        "staff_notes": "تم التنسيق وحضور الفني سجاد وتم إنجاز العمل وموازنة الأحمال بنجاح.",
        "phone": "+9647809900112",
        "email": "fatima.client@example.com",
        "price": Decimal("25000.00"),
    },
    {
        "service_slug": "ac-split-cleaning-repair-gas-refill",
        "customer": created_customers["fatima_client"],
        "status": ServiceRequest.Status.IN_PROGRESS,
        "notes": "صيانة وغسيل عدد 2 سبلت جنرال في الطابق الأول مع فحص الغاز.",
        "staff_notes": "الفني في الطريق إلى الموقع، تم تجهيز معدات الضغط والغاز.",
        "phone": "+9647809900112",
        "email": "fatima.client@example.com",
        "price": Decimal("60000.00"),
    },
    {
        "service_slug": "leak-detection-plumbing-repairs-baghdad",
        "customer": created_customers["ali_client"],
        "status": ServiceRequest.Status.DONE,
        "notes": "تسريب مياه في حمام الطابق الأرضي بحاجة لكشف إلكتروني مستعجل باليرموك.",
        "staff_notes": "تم الكشف وتبديل وصلة البايب الحراري بنجاح.",
        "phone": "+9647708899001",
        "email": "ali.client@example.com",
        "price": Decimal("35000.00"),
    },
    {
        "service_slug": "custom-ecommerce-store-zaincash-delivery",
        "customer": created_customers["omar_client"],
        "status": ServiceRequest.Status.IN_REVIEW,
        "notes": "نرغب بتطوير متجر إلكتروني لبيع العطور ومستحضرات التجميل مع ربط الدفع والتوصيل.",
        "staff_notes": "تمت مراجعة المتطلبات وجاري الاتصال بالعميل لمناقشة التصميم.",
        "phone": "+9647710011223",
        "email": "omar.client@example.com",
        "price": Decimal("280.00"),
    },
    {
        "service_slug": "mobile-car-computer-diagnostics-basra",
        "customer": created_customers["ali_client"],
        "status": ServiceRequest.Status.NEW,
        "notes": "أحتاج فحص كمبيوتر وصبغ لسيارة كيا سورينتو موديل 2021 في معارض البصرة غداً صباحاً.",
        "staff_notes": "",
        "phone": "+9647708899001",
        "email": "ali.client@example.com",
        "price": Decimal("35000.00"),
    }
]

for req_data in REQUESTS_SEED:
    try:
        svc = Service.objects.get(slug=req_data["service_slug"])
        sr, created = ServiceRequest.objects.get_or_create(
            service=svc,
            customer=req_data["customer"],
            status=req_data["status"],
            defaults={
                "customer_notes": req_data["notes"],
                "staff_notes": req_data["staff_notes"],
                "contact_phone": req_data["phone"],
                "contact_email": req_data["email"],
                "price": req_data["price"],
            }
        )
        print(f"  📑 Order created: #{sr.id} for [{svc.title[:25]}...] Status: {sr.get_status_display()}")
    except Service.DoesNotExist:
        pass

# ============================================================================
# 5. Conversations & Chat Messages
# ============================================================================
print("\n💬 Seeding Conversations & Messages...")

# Conv 1: Fatima (Customer) & Sajjad (Provider)
fatima_user = created_customers["fatima_client"]
sajjad_user = created_providers["sajjad_electric"].user
sajjad_svc = Service.objects.filter(provider=created_providers["sajjad_electric"]).first()

conv1, _ = Conversation.objects.get_or_create(
    sender=fatima_user,
    receiver=sajjad_user,
    defaults={'service': sajjad_svc}
)

m1, _ = Message.objects.get_or_create(
    conversation=conv1,
    sender=fatima_user,
    content="السلام عليكم أستاذ سجاد، عندي سبلت يطفي بعد 10 دقائق من التشغيل، متى متاح حضرتك لتفحصه؟",
    defaults={'is_read': True}
)
m2, _ = Message.objects.get_or_create(
    conversation=conv1,
    sender=sajjad_user,
    content="وعليكم السلام أختي، على الأغلب المشكلة ضعف بالفولتية أو الكابستر يحتاج تبديل. إن شاء الله أكون عندكم اليوم الساعة 4 عصراً.",
    defaults={'is_read': True}
)
m3, _ = Message.objects.get_or_create(
    conversation=conv1,
    sender=fatima_user,
    content="ممتاز أستاذ، العنوان بالبصرة حي الجزائر قرب المستشفى. بانتظارك وجزاك الله خيراً.",
    defaults={'is_read': True}
)
conv1.last_message = m3
conv1.save()

# Conv 2: Omar (Customer) & Ahmed (Tech Provider)
omar_user = created_customers["omar_client"]
ahmed_user = created_providers["ahmed_tech"].user
ahmed_svc = Service.objects.filter(provider=created_providers["ahmed_tech"]).first()

conv2, _ = Conversation.objects.get_or_create(
    sender=omar_user,
    receiver=ahmed_user,
    defaults={'service': ahmed_svc}
)

m4, _ = Message.objects.get_or_create(
    conversation=conv2,
    sender=omar_user,
    content="مرحباً مهندس أحمد، بخصوص متجر العطور، هل البوابة تدعم حساب التاجر المباشر مع زين كاش؟",
    defaults={'is_read': True}
)
m5, _ = Message.objects.get_or_create(
    conversation=conv2,
    sender=ahmed_user,
    content="أهلاً أستاذ عمر، نعم بكل تأكيد نقوم بربط الـ Merchant API الرسمي لزين كاش وتصل المبالغ لمحفظتكم فوراً مع تقرير مبيعات يومي.",
    defaults={'is_read': True}
)
conv2.last_message = m5
conv2.save()

print("  ✅ Conversations and chat messages created successfully.")

# ============================================================================
# 6. Favorites & Wallet Transactions
# ============================================================================
print("\n❤️ Seeding Favorites & Financial Transactions...")

for svc in created_services[:4]:
    FavoriteService.objects.get_or_create(user=fatima_user, service=svc)
for svc in created_services[2:6]:
    FavoriteService.objects.get_or_create(user=omar_user, service=svc)

# Transactions for Sajjad
w_sajjad = Wallet.objects.filter(user=sajjad_user).first()
if w_sajjad:
    Transaction.objects.get_or_create(
        wallet=w_sajjad,
        amount=Decimal("50000.00"),
        transaction_type=Transaction.TransactionType.ORDER_EARNING,
        defaults={
            "description": "أرباح إنجاز طلب صيانة كهرباء رقم #1",
            "status": Transaction.TransactionStatus.COMPLETED,
        }
    )
    Transaction.objects.get_or_create(
        wallet=w_sajjad,
        amount=Decimal("60000.00"),
        transaction_type=Transaction.TransactionType.ORDER_EARNING,
        defaults={
            "description": "أرباح غسيل وتعبئة غاز سبلت رقم #2",
            "status": Transaction.TransactionStatus.COMPLETED,
        }
    )

print("  ✅ Favorites and financial transactions seeded.")

print("\n" + "="*70)
print("🎉 ALL DEMO DATA & ACCOUNTS SUCCESSFULLY SEEDED!")
print("="*70)
print(f"Master Password for all Demo Accounts:  {DEMO_PASSWORD}")
print("\nDemo Providers:")
for p in PROVIDERS_DATA:
    print(f"  - @{p['username']} ({p['first_name']} {p['last_name']}) -> {p['title']} [{p['city']}]")

print("\nDemo Customers:")
for c in CUSTOMERS_DATA:
    print(f"  - @{c['username']} ({c['first_name']} {c['last_name']}) -> {c['city']}")

print(f"\nAdmin Superuser:")
print(f"  - @munt (Superuser)")
print("="*70)
