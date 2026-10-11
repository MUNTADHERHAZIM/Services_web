# +-----------------------------------------------------------------------+
# |  ملف إعدادات WSGI لخدمة PythonAnywhere - منصة خدماتي                |
# |  قم بنسخ محتوى هذا الملف ولصقه في ملف WSGI الخاص بحسابك في          |
# |  لوحة تحكم PythonAnywhere (قسم Web -> WSGI configuration file)        |
# +-----------------------------------------------------------------------+

import os
import sys

# 1. تحديد مسار المشروع (استبدل 'yourusername' باسم المستخدم الخاص بك في PythonAnywhere)
# اسم المجلد هو Services_web لأنك قمت بعمل clone للمستودع بهذا الاسم
project_home = '/home/yourusername/Services_web'

if project_home not in sys.path:
    sys.path.append(project_home)

# 2. تعيين ملف إعدادات دجانغو
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# 3. متغيرات الإنتاج (يمكن تفعيلها بإزالة علامة # وتعيين مفتاح سري قوي)
# os.environ['DJANGO_DEBUG'] = 'False'
# os.environ['DJANGO_SECRET_KEY'] = 'change-this-to-a-very-secure-secret-key-in-production'

# 4. تشغيل تطبيق WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
