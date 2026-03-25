# نظام عرض الخدمات - Service Catalog System

نظام متكامل لعرض وإدارة الخدمات مبني بـ Django 5 مع دعم كامل للغة العربية و RTL.

## المميزات

### للمستخدمين
- ✅ تصفح الخدمات مع البحث والفلترة
- ✅ عرض تفاصيل الخدمات والتقييمات
- ✅ تقديم طلبات الخدمات
- ✅ متابعة حالة الطلبات
- ✅ نظام إشعارات

### للإدارة
- ✅ لوحة تحكم مع إحصائيات
- ✅ إدارة الخدمات والتصنيفات
- ✅ إدارة الطلبات وتحديث الحالات
- ✅ إدارة مقدمي الخدمات
- ✅ لوحة Admin احترافية

## المتطلبات

- Python 3.10+
- Django 5.0+
- PostgreSQL (أو SQLite للتطوير)

## التثبيت والتشغيل المحلي

### 1. إنشاء بيئة افتراضية

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 3. تشغيل Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. إنشاء مستخدم Admin

```bash
python manage.py createsuperuser
```

### 5. تشغيل السيرفر

```bash
python manage.py runserver
```

الموقع متاح على: http://127.0.0.1:8000

لوحة الإدارة: http://127.0.0.1:8000/admin

## إضافة بيانات تجريبية

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import Provider
from services.models import Category, Service

# إنشاء تصنيفات
cat1 = Category.objects.create(name='تصميم', slug='design', icon='bi-palette', is_active=True)
cat2 = Category.objects.create(name='برمجة', slug='programming', icon='bi-code-slash', is_active=True)
cat3 = Category.objects.create(name='تسويق', slug='marketing', icon='bi-megaphone', is_active=True)

# إنشاء مقدم خدمة
user = User.objects.create_user('provider1', 'provider@test.com', 'password123')
provider = Provider.objects.create(user=user, display_name='أحمد محمد', bio='مصمم محترف', is_verified=True)

# إنشاء خدمات
Service.objects.create(
    category=cat1,
    provider=provider,
    title='تصميم شعار احترافي',
    slug='logo-design',
    summary='تصميم شعار مميز لشركتك',
    description='نقدم خدمة تصميم شعارات احترافية بأفكار مبتكرة.',
    price=500,
    is_active=True,
    is_featured=True
)
```

## هيكل المشروع

```
ail_project/
├── config/              # إعدادات Django
├── accounts/            # إدارة المستخدمين والمقدمين
├── services/            # الخدمات والتصنيفات
├── requests/            # طلبات الخدمات
├── dashboard/           # لوحة تحكم الموظفين
├── core/                # الصفحات الأساسية
├── templates/           # قوالب HTML
├── static/              # ملفات CSS/JS
└── media/               # الملفات المرفوعة
```

## التقنيات المستخدمة

- **Backend**: Django 5
- **Database**: PostgreSQL / SQLite
- **Frontend**: Bootstrap 5 RTL
- **Icons**: Bootstrap Icons
- **Fonts**: Tajawal (Google Fonts)

## Phase 2 - التحسينات المستقبلية

- [ ] REST API مع Django REST Framework
- [ ] JWT Authentication للـ API
- [ ] Celery لإشعارات البريد الإلكتروني
- [ ] نظام تقييم متكامل
- [ ] رفع صور متعدد مع Cloudinary/S3
- [ ] Charts في لوحة التحكم
- [ ] نظام دفع إلكتروني
- [ ] إشعارات فورية مع Django Channels

## المطور MUNTADHER HAZIM THAMER

