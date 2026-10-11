"""
Seed Full Services Catalog - بذر شجرة التصنيفات والخدمات الشاملة (12 قسماً رئيساً مع الأقسام الفرعية والأيقونات)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category, Service

CATALOG = [
    {
        "name": "خدمات المنزل والصيانة",
        "slug": "home-maintenance",
        "icon": "bi-house-gear-fill",
        "order": 1,
        "description": "حلول متكاملة لصيانة وإصلاح كافة أعمال المنزل والمنشآت من سباكة وكهرباء وتكييف ونظافة بأعلى جودة.",
        "subcategories": [
            {"name": "سباكة", "slug": "plumbing", "icon": "bi-droplet-half", "order": 1, "description": "تسربات المياه، تركيب خلاطات، صيانة سخانات، وتأسيس وترميم حمامات."},
            {"name": "كهرباء", "slug": "electricity", "icon": "bi-lightning-charge-fill", "order": 2, "description": "تمديدات كهربائية، إصلاح أعطال، إنارة ديكورية، وصيانة لوحات الكهرباء."},
            {"name": "تكييف وتبريد", "slug": "hvac-cooling", "icon": "bi-snow", "order": 3, "description": "تركيب مكيفات سبليت وشباك، صيانة، غسيل وتنظيف، وتعبئة غاز فريون."},
            {"name": "نجارة", "slug": "carpentry", "icon": "bi-hammer", "order": 4, "description": "أبواب، شبابيك، تفصيل خزائن، صيانة مطابخ، وفك وتركيب أثاث."},
            {"name": "ألمنيوم وزجاج", "slug": "aluminum-glass", "icon": "bi-window-split", "order": 5, "description": "شبابيك ألمنيوم، واجهات زجاجية، أبواب سحاب وزجاج سيكوريت مقاوم."},
            {"name": "دهان وديكور", "slug": "painting-decor", "icon": "bi-paint-bucket", "order": 6, "description": "دهانات داخلية وخارجية، ورق جدران، أعمال جبس بورد، وأسقف مستعارة."},
            {"name": "بناء وترميم", "slug": "construction-renovation", "icon": "bi-bricks", "order": 7, "description": "تركيب بلاط، سيراميك، رخام، تكسير وترميم حمامات ومطابخ ومباني."},
            {"name": "تنظيف", "slug": "cleaning-services", "icon": "bi-stars", "order": 8, "description": "تنظيف منازل وشقق، غسيل مفروشات وسجاد، تنظيف خزانات، مسابح، وواجهات."},
            {"name": "مكافحة حشرات وتعقيم", "slug": "pest-control", "icon": "bi-shield-shaded", "order": 9, "description": "رش مبيدات آمنة، مكافحة حشرات وقوارض، وتعقيم منازل وشركات مع الضمان."},
            {"name": "صيانة أجهزة منزلية", "slug": "appliance-repair", "icon": "bi-gear-wide-connected", "order": 10, "description": "صيانة فورية للغسالات، الثلاجات، الأفران، والمجففات ومختلف الأجهزة."},
        ]
    },
    {
        "name": "خدمات السيارات",
        "slug": "car-services",
        "icon": "bi-car-front-fill",
        "order": 2,
        "description": "عناية متكاملة لسيارتك من ميكانيكا وفحص كمبيوتر وصيانة دورية وسطحات وإنقاذ سريع.",
        "subcategories": [
            {"name": "ميكانيكا وكهرباء سيارات", "slug": "car-mechanics", "icon": "bi-wrench-adjustable", "order": 1, "description": "صيانة محركات، قير، فرامل، أعطال دينامو وبطاريات وكهرباء عامة."},
            {"name": "فحص كمبيوتر وبرمجة", "slug": "car-diagnostics", "icon": "bi-cpu", "order": 2, "description": "كشف أعطال بالكمبيوتر، برمجة حساسات، ريموتات، وشرائح إلكترونية."},
            {"name": "تغيير زيت، إطارات، بطاريات", "slug": "car-oil-tires-battery", "icon": "bi-disc", "order": 3, "description": "خدمات الصيانة السريعة لتغيير الزيوت والفلاتر، ميزان الإطارات وتركيب البطاريات."},
            {"name": "غسيل وتلميع", "slug": "car-wash-detailing", "icon": "bi-water", "order": 4, "description": "غسيل بخار متنقل، تلميع ساطع خارجي، تنظيف فرش داخلي ونانو سيراميك."},
            {"name": "سمكرة ودهان", "slug": "car-body-repair", "icon": "bi-brush", "order": 5, "description": "تعديل صدمات على البارد، سمكرة احترافية، ورش فرن مطابقة للون الوكالة."},
            {"name": "إصلاح زجاج وتبديل", "slug": "car-glass-repair", "icon": "bi-shield", "order": 6, "description": "معالجة شروخ الزجاج الأمامي، وتبديل زجاج السيارات الأصلي مع العوازل."},
            {"name": "سحب سيارة / ونش", "slug": "car-towing", "icon": "bi-truck-flatbed", "order": 7, "description": "سطحات هيدروليك وونشات إنقاذ لسحب السيارات المعطلة على مدار 24 ساعة."},
            {"name": "فحص سيارة قبل الشراء", "slug": "car-inspection-check", "icon": "bi-clipboard-check", "order": 8, "description": "فحص شامل ودقيق للبدي والمكينة والشاصي مع تقرير تقني مفصل قبل الشراء."},
            {"name": "خدمات متنقلة للسيارات", "slug": "car-mobile-services", "icon": "bi-geo-alt-fill", "order": 9, "description": "ورشة متنقلة تصلك لموقعك لإصلاح الإطارات وشحن البطارية وتبديل الزيت على الطريق."},
        ]
    },
    {
        "name": "التقنية والبرمجة",
        "slug": "tech-programming",
        "icon": "bi-code-slash",
        "order": 3,
        "description": "حلول برمجية وتقنية متقدمة تشمل المواقع، التطبيقات، السيرفرات والذكاء الاصطناعي.",
        "subcategories": [
            {"name": "تصميم مواقع ومتاجر إلكترونية", "slug": "web-ecommerce-dev", "icon": "bi-globe2", "order": 1, "description": "برمجة متاجر سلة وزد وشوبيفاي، وتطوير مواقع احترافية متوافقة مع الجوال."},
            {"name": "تطبيقات جوال", "slug": "mobile-apps", "icon": "bi-phone", "order": 2, "description": "بناء تطبيقات Flutter و iOS و Android متكاملة وسلسة الاستخدام."},
            {"name": "أنظمة إدارة وبرامج مخصصة", "slug": "custom-software-erp", "icon": "bi-hdd-network", "order": 3, "description": "تطوير أنظمة ERP وبرامج نقاط بيع POS وإدارة المخازن والمبيعات."},
            {"name": "صيانة كمبيوتر ولابتوب وطابعات", "slug": "computer-printer-repair", "icon": "bi-pc-display", "order": 4, "description": "تسريع الأجهزة، فرمتة وتثبيت ويندوز/ماك، وصيانة هاردوير الطابعات والأجهزة."},
            {"name": "شبكات وإنترنت وكاميرات مراقبة", "slug": "networks-surveillance", "icon": "bi-router", "order": 5, "description": "تمديد شبكات LAN و WiFi وكاميرات مراقبة IP ذكية مع ربطها بالجوال."},
            {"name": "استضافة ودومينات وسيرفرات", "slug": "hosting-cloud-servers", "icon": "bi-server", "order": 6, "description": "حجز دومينات، إدارة سيرفرات لينكس/ويندوز وحلول استضافة سحابية فائقة السرعة."},
            {"name": "أمن سيبراني وحماية بيانات", "slug": "cybersecurity-protection", "icon": "bi-shield-lock-fill", "order": 7, "description": "فحص ثغرات المواقع وتأمين خوادم وقواعد البيانات ضد الاختراقات."},
            {"name": "استعادة بيانات ونسخ احتياطي", "slug": "data-recovery-backup", "icon": "bi-database-fill-up", "order": 8, "description": "استرجاع الملفات المحذوفة من الأقراص الصلبة والفلاشات وإعداد النسخ الاحتياطي."},
            {"name": "أتمتة وذكاء اصطناعي", "slug": "ai-automation", "icon": "bi-robot", "order": 9, "description": "بناء شات بوت ذكي، أتمتة العمليات اليومية ودمج تقنيات ChatGPT و AI بالأنظمة."},
        ]
    },
    {
        "name": "التصميم والتسويق",
        "slug": "design-marketing",
        "icon": "bi-palette-fill",
        "order": 4,
        "description": "إبداع بصري وتسويق رقمي مدروس لمضاعفة مبيعاتك وبناء هوية علامتك التجارية.",
        "subcategories": [
            {"name": "تصميم شعار وهوية بصرية", "slug": "branding-identity", "icon": "bi-vector-pen", "order": 1, "description": "ابتكار لوجو مميز، أدلة الهوية البصرية، بزنس كارد وكافة ملحقات البراند."},
            {"name": "إدارة سوشيال ميديا", "slug": "social-media-management", "icon": "bi-share-fill", "order": 2, "description": "تخطيط ونشر المحتوى، إدارة الحسابات، وزيادة التفاعل والمتابعين الحقيقيين."},
            {"name": "إعلانات ممولة", "slug": "paid-ads", "icon": "bi-badge-ad-fill", "order": 3, "description": "حملات إعلانية عالية العائد على الاستثمار في تيك توك، إنستغرام، سناب شات وجوجل."},
            {"name": "تحسين محركات البحث SEO", "slug": "seo-services", "icon": "bi-search", "order": 4, "description": "تصدر النتائج الأولى في محرك بحث جوجل لموقعك أو متجرك الإلكتروني."},
            {"name": "كتابة محتوى وترجمة", "slug": "content-copywriting-translation", "icon": "bi-file-earmark-text-fill", "order": 5, "description": "نصوص إعلانية مقنعة، مقالات تسويقية متوافقة مع السيو، وترجمة احترافية."},
            {"name": "مونتاج فيديو وموشن جرافيك", "slug": "video-editing-motion", "icon": "bi-camera-reels-fill", "order": 6, "description": "تحرير فيديوهات ريلز وتيك توك، مقاطع يوتيوب وفيديوهات موشن جرافيك ترويجية."},
            {"name": "تصوير منتجات ومناسبات", "slug": "commercial-photography", "icon": "bi-camera-fill", "order": 7, "description": "جلسات تصوير دعائية للمنتجات والمطاعم والفعاليات بأعلى دقة احترافية."},
        ]
    },
    {
        "name": "التعليم والتدريب",
        "slug": "education-training",
        "icon": "bi-mortarboard-fill",
        "order": 5,
        "description": "تعلّم وتطوير مستمر مع نخبة من أفضل المدرسين والمدربين المعتمدين لمختلف المجالات.",
        "subcategories": [
            {"name": "دروس خصوصية: رياضيات، علوم، لغات", "slug": "private-tutoring", "icon": "bi-book-half", "order": 1, "description": "متابعة مدرسية وجامعية في الرياضيات، الفيزياء، الكيمياء، الإنجليزية والفرنسية."},
            {"name": "دورات برمجة وتصميم", "slug": "coding-design-courses", "icon": "bi-terminal-fill", "order": 2, "description": "كورسات عملية لتعلم بايثون، تطوير المواقع، UI/UX والتصميم بالفوتوشوب والإليستريتور."},
            {"name": "دورات تسويق وإدارة", "slug": "marketing-management-courses", "icon": "bi-graph-up-arrow", "order": 3, "description": "تدريب عملي على التسويق الإلكتروني، إدارة الأعمال، واستراتيجيات البيع الحديثة."},
            {"name": "دورات مهنية وشهادات", "slug": "vocational-certifications", "icon": "bi-award-fill", "order": 4, "description": "تحضير مكثف لاختبارات PMP، IELTS، المحاسبة المهنية والشهادات المعتمدة."},
            {"name": "موسيقى، رسم، طبخ، لياقة", "slug": "arts-lifestyle-courses", "icon": "bi-music-note-beamed", "order": 5, "description": "دورات ممتعة لتعلم العزف، فنون الرسم، مهارات الطبخ، واللياقة البدنية."},
            {"name": "تدريب شركات وموظفين", "slug": "corporate-training", "icon": "bi-building-fill-gear", "order": 6, "description": "برامج تدريبية مخصصة لرفع كفاءة موظفي الشركات وفرق خدمة العملاء والمبيعات."},
        ]
    },
    {
        "name": "النقل والخدمات اللوجستية",
        "slug": "logistics-moving",
        "icon": "bi-truck",
        "order": 6,
        "description": "حلول نقل وشحن وتوصيل سريعة وآمنة مع ضمان سلامة كافة المنقولات والأغراض.",
        "subcategories": [
            {"name": "نقل أثاث مع الفك والتركيب", "slug": "furniture-moving-assembly", "icon": "bi-box-seam-fill", "order": 1, "description": "دينا نقل عفش مجهزة مع فنيين متخصصين لفك وتغليف وتركيب غرف النوم والمطابخ."},
            {"name": "توصيل طلبات ومشتريات", "slug": "order-delivery", "icon": "bi-bicycle", "order": 2, "description": "مندوب توصيل سريع للطرود والهدايا والمشتريات بين مختلف المناطق."},
            {"name": "شحن داخلي وخارجي", "slug": "shipping-cargo", "icon": "bi-box2-fill", "order": 3, "description": "خدمات الشحن البري والجوي للبضائع والطرود بأسعار تنافسية وتتبع لحظي."},
            {"name": "نقل سيارات ومعدات", "slug": "heavy-transportation", "icon": "bi-truck-front", "order": 4, "description": "نقل المركبات والمعدات الثقيلة عبر سطحات مخصصة لمختلف المدن."},
            {"name": "تخزين وتغليف", "slug": "storage-packaging", "icon": "bi-archive-fill", "order": 5, "description": "مستودعات تخزين أثاث آمنة ومكيفة، وتوفير مواد كراتين وبابلز التغليف."},
            {"name": "خدمات عمال تحميل وتنزيل", "slug": "moving-labor", "icon": "bi-person-walking", "order": 6, "description": "عمالة قوية ومدربة لمساعدة الأفراد والشركات في شحن وتفريغ البضائع والأثاث."},
        ]
    },
    {
        "name": "المناسبات",
        "slug": "events-weddings",
        "icon": "bi-balloon-fill",
        "order": 7,
        "description": "تجهيز وتنظيم وتصوير المناسبات والحفلات بأرقى الديكورات وأشهى المأكولات والضيافة.",
        "subcategories": [
            {"name": "تصوير فوتوغرافي وفيديو", "slug": "event-photography", "icon": "bi-camera-fill", "order": 1, "description": "تصوير أفراح ومؤتمرات ولقاءات بدقة 4K مع استخدام طائرات الدرون والإضاءة السينمائية."},
            {"name": "قاعات وخيام وتجهيزات", "slug": "event-venues-tents", "icon": "bi-house-heart", "order": 2, "description": "تأجير وتجهيز قاعات، خيام مناسبات مكيفة، كراسي، طاولات ومسارح."},
            {"name": "ديكور وإضاءة", "slug": "event-decor-lighting", "icon": "bi-lightbulb-fill", "order": 3, "description": "كوشات أفراح فخمة، تنسيق ورود طبيعية، إضاءات مسرحية وبوابات استقبال."},
            {"name": "ضيافة وطعام وحلويات", "slug": "event-catering", "icon": "bi-cup-hot-fill", "order": 4, "description": "بوفيهات مفتوحة، صبابين قهوة وشاي، حلويات ومقبلات تلائم أرقى المناسبات."},
            {"name": "تنظيم حفلات ومؤتمرات", "slug": "event-planning-management", "icon": "bi-calendar-event-fill", "order": 5, "description": "تخطيط شامل وإدارة كاملة للحفلات التخرج، المؤتمرات، والمعارض الرسمية."},
            {"name": "دي جي وفرق فنية", "slug": "event-dj-performers", "icon": "bi-speaker-fill", "order": 6, "description": "أنظمة صوت ومكبرات صوت متطورة، دي جي، وفقرات ترفيهية واستعراضية."},
            {"name": "تنسيق أعراس ومناسبات", "slug": "wedding-coordination", "icon": "bi-gem", "order": 7, "description": "خدمة منسقة الأعراس الخاصة لإدارة وتنسيق كافة تفاصيل حفل الزفاف خطوة بخطوة."},
        ]
    },
    {
        "name": "الصحة والجمال",
        "slug": "health-beauty",
        "icon": "bi-heart-pulse-fill",
        "order": 8,
        "description": "خدمات رعاية صحية وتجميلية منزلية متخصصة لراحتك ورفاهيتك وجمالك اليومي.",
        "subcategories": [
            {"name": "تمريض منزلي", "slug": "home-nursing", "icon": "bi-capsule", "order": 1, "description": "ممرضون وممرضات مرخصون لرعاية المرضى، إعطاء الحقن، وغيارات العمليات بالمنزل."},
            {"name": "علاج طبيعي", "slug": "physical-therapy", "icon": "bi-person-arms-up", "order": 2, "description": "جلسات علاج طبيعي وتأهيل حركي منزلي لمشاكل العمود الفقري والمفاصل والجلطات."},
            {"name": "مدرب شخصي وتغذية", "slug": "personal-trainer-nutrition", "icon": "bi-activity", "order": 3, "description": "برامج تدريب لياقة بدنية منزلية أو أونلاين وجداول دايت مدروسة للوصول لوزنك المثالي."},
            {"name": "حلاقة رجالية ونسائية", "slug": "hair-grooming", "icon": "bi-scissors", "order": 4, "description": "حلاقة وقص شعر واستشوار منزلي للرجال والأطفال أو حجز صالونات متخصصة."},
            {"name": "مكياج وتجميل", "slug": "makeup-beauty", "icon": "bi-brush", "order": 5, "description": "ميك أب سهرات وأعراس، تنظيف بشرة، تركيب رموش وعناية بالأظافر مع خبيرات تجميل."},
            {"name": "مساج وسبا", "slug": "massage-spa", "icon": "bi-flower1", "order": 6, "description": "جلسات مساج سويدي وعلاجي واسترخائي بالزيوت الطبيعية في منزلك."},
            {"name": "رعاية كبار السن وذوي الاحتياجات", "slug": "elderly-special-care", "icon": "bi-heart-fill", "order": 7, "description": "مرافقون مؤهلون لمساعدة كبار السن وذوي الإعاقة في الأنشطة اليومية والتنقل."},
        ]
    },
    {
        "name": "الأعمال والخدمات المهنية",
        "slug": "business-professional",
        "icon": "bi-briefcase-fill",
        "order": 9,
        "description": "خدمات المحاسبة، القانون، والاستشارات الإدارية لمساعدة شركتك ومشروعك على النمو والامتثال.",
        "subcategories": [
            {"name": "محاسبة وضرائب", "slug": "accounting-tax", "icon": "bi-calculator-fill", "order": 1, "description": "إعداد القوائم المالية، مسك الدفاتر، تقديم إقرارات ضريبة القيمة المضافة والزكاة."},
            {"name": "استشارات قانونية وعقود", "slug": "legal-contracts", "icon": "bi-file-earmark-lock-fill", "order": 2, "description": "صياغة وتدقيق العقود والاتفاقيات، الاستشارات العمالية، وتأسيس وتسجيل الشركات."},
            {"name": "دراسات جدوى واستشارات إدارية", "slug": "feasibility-management", "icon": "bi-clipboard-data-fill", "order": 3, "description": "دراسات جدوى اقتصادية وسوقية معتمدة لتقديمها للمستثمرين وصناديق التمويل."},
            {"name": "موارد بشرية وتوظيف", "slug": "hr-recruitment", "icon": "bi-people-fill", "order": 4, "description": "استقطاب الكفاءات، عمل المقابلات، إعداد سلم الرواتب واللوائح التنظيمية للعمل."},
            {"name": "إدخال بيانات وسكرتارية", "slug": "data-entry-secretarial", "icon": "bi-keyboard-fill", "order": 5, "description": "تفريغ الملفات على إكسل، إدارة البريد، وتنسيق المواعيد عبر سكرتارية احترافية."},
            {"name": "طباعة وتغليف وتصميم مطبوعات", "slug": "printing-packaging", "icon": "bi-printer-fill", "order": 6, "description": "تصميم وطباعة الفواتير، البروشورات، الأكياس والعلب الكرتونية المخصصة."},
            {"name": "خدمات حكومية وتعقيب معاملات", "slug": "gov-services-clearance", "icon": "bi-bank2", "order": 7, "description": "تخليص وتجديد التراخيص والسجلات التجارية ومنصات الأعمال الرسمية."},
        ]
    },
    {
        "name": "الحيوانات",
        "slug": "pets-veterinary",
        "icon": "bi-feather",
        "order": 10,
        "description": "رعاية طبية وعناية بيطرية فائقة لحيواناتك الأليفة في المنزل وفي العيادات المعتمدة.",
        "subcategories": [
            {"name": "بيطري منزلي", "slug": "home-vet", "icon": "bi-heart-pulse", "order": 1, "description": "زيارة الطبيب البيطري لمنزلك لفحص القطط والكلاب وتشخيص الأمراض وتقديم العلاج."},
            {"name": "تطعيم ورعاية", "slug": "pet-vaccination", "icon": "bi-shield-shaded", "order": 2, "description": "برامج التطعيمات الدورية، الفيتامينات، ومكافحة الطفيليات مع استخراج الشهادات الصحية."},
            {"name": "تدريب حيوانات", "slug": "pet-training", "icon": "bi-award", "order": 3, "description": "تدريب طاعة وتعديل سلوك للكلاب والحيوانات الأليفة مع مدربين متخصصين."},
            {"name": "تنظيف وتجميل", "slug": "pet-grooming", "icon": "bi-scissors", "order": 4, "description": "حلاقة شعر، استحمام طبي، تنظيف الأذن وتقليم الأظافر في منزلك أو بالصالون."},
            {"name": "نزهة ورعاية مؤقتة", "slug": "pet-sitting-walking", "icon": "bi-clock-history", "order": 5, "description": "استضافة الحيوانات الأليفة أثناء سفرك ومرافقتها في جولات المشي اليومية."},
        ]
    },
    {
        "name": "خدمات شخصية وإدارية",
        "slug": "personal-administrative",
        "icon": "bi-person-check-fill",
        "order": 11,
        "description": "مساعدات يومية وتسهيل للمهام المنزلية والشخصية لتوفير وقتك وجهدك في كل لحظة.",
        "subcategories": [
            {"name": "رعاية أطفال", "slug": "babysitting-childcare", "icon": "bi-emoji-smile", "order": 1, "description": "جليسات أطفال ومربيات معتمدات وموثوقات للعناية بأطفالك في المنزل بأمان."},
            {"name": "تنظيف وغسيل وكي", "slug": "laundry-ironing", "icon": "bi-water", "order": 2, "description": "خدمات غسيل وكي الملابس والستائر والمفارش مع الاستلام والتوصيل السريع."},
            {"name": "تسوق وتوصيل", "slug": "errands-shopping", "icon": "bi-cart-check-fill", "order": 3, "description": "شراء احتياجاتك من السوبرماركت والصيدلية وقضاء كافة المشاوير عنك."},
            {"name": "مرافقة مرضى", "slug": "patient-companion", "icon": "bi-heart-fill", "order": 4, "description": "مرافق صحي للمرضى أثناء المراجعات الطبية والتحاليل في المستشفيات والمراكز."},
            {"name": "أمن وحراسة", "slug": "security-guard", "icon": "bi-shield-check", "order": 5, "description": "تأمين حراسات شخصية وحراس أمن للمباني والفعاليات الخاصة."},
            {"name": "خدمات طارئة: كهرباء، سباكة، فتح أقفال، سحب سيارة", "slug": "emergency-services", "icon": "bi-exclamation-triangle-fill", "order": 6, "description": "فريق طوارئ سريع متوفر على مدار الساعة لأعطال الكهرباء والسباكة وفتح الأبواب المغلقة."},
        ]
    },
    {
        "name": "خدمات عن بعد",
        "slug": "remote-freelance",
        "icon": "bi-laptop",
        "order": 12,
        "description": "إنجاز أعمالك أونلاين بالكامل عبر خبراء ومستقلين في التصميم، الترجمة، البرمجة والاستشارات.",
        "subcategories": [
            {"name": "تصميم، برمجة، تسويق", "slug": "remote-design-code-marketing", "icon": "bi-display", "order": 1, "description": "خدمات رقمية متكاملة يتم تسليمها بالكامل عن بعد بجودة وسرعة استثنائية."},
            {"name": "ترجمة، كتابة، تدقيق", "slug": "remote-translation-proofreading", "icon": "bi-pen-fill", "order": 2, "description": "كتابة أبحاث، تدقيق لغوي عربي وإنجليزي وترجمة معتمدة مع تسليم إلكتروني."},
            {"name": "استشارات، تدريب أونلاين", "slug": "remote-consulting-coaching", "icon": "bi-camera-video-fill", "order": 3, "description": "جلسات استشارية فردية وجماعية عبر Zoom أو Google Meet في مختلف التخصصات."},
            {"name": "محاسبة ودعم فني", "slug": "remote-accounting-support", "icon": "bi-headset", "order": 4, "description": "دعم فني ومحاسبي عن بعد لحل مشاكل البرامج والسيرفرات في أسرع وقت."},
        ]
    }
]

def seed():
    print("Starting category and subcategory seed...")
    
    # Map old categories if needed
    category_mapping = {
        'تصميم جرافيك': ('design-marketing', 'branding-identity'),
        'تطوير ويب': ('tech-programming', 'web-ecommerce-dev'),
        'تسويق رقمي': ('design-marketing', 'paid-ads'),
        'خدمات منزلية': ('home-maintenance', 'cleaning-services'),
    }

    created_main = 0
    created_sub = 0

    for cat_data in CATALOG:
        main_cat, m_created = Category.objects.update_or_create(
            slug=cat_data["slug"],
            defaults={
                "name": cat_data["name"],
                "icon": cat_data["icon"],
                "order": cat_data["order"],
                "description": cat_data["description"],
                "is_active": True,
                "parent": None
            }
        )
        if m_created:
            created_main += 1
            print(f"Created main category: {main_cat.name}")
        else:
            print(f"Updated main category: {main_cat.name}")

        for sub_data in cat_data["subcategories"]:
            sub_cat, s_created = Category.objects.update_or_create(
                slug=sub_data["slug"],
                defaults={
                    "name": sub_data["name"],
                    "icon": sub_data["icon"],
                    "order": sub_data["order"],
                    "description": sub_data["description"],
                    "is_active": True,
                    "parent": main_cat
                }
            )
            if s_created:
                created_sub += 1

    # Attach existing services to the new subcategories if needed
    for old_name, (m_slug, s_slug) in category_mapping.items():
        old_cat = Category.objects.filter(name=old_name).first()
        target_sub = Category.objects.filter(slug=s_slug).first()
        if old_cat and target_sub and old_cat.id != target_sub.id:
            services = Service.objects.filter(category=old_cat)
            count = services.count()
            if count > 0:
                services.update(category=target_sub)
                print(f"Moved {count} services from '{old_name}' to '{target_sub.name}'")
            # If old_cat has no more services and isn't in main catalog, can delete or mark inactive
            if old_cat.services.count() == 0 and old_cat.parent is None and old_cat.slug not in [c['slug'] for c in CATALOG]:
                old_cat.delete()
                print(f"Cleaned up legacy category '{old_name}'")

    print(f"\nDone! Seeded/Updated 12 Main Categories and {created_sub} Subcategories.")

if __name__ == '__main__':
    seed()
