"""
Core Validators - أدوات التحقق الصارم من المدخلات
دعم التحقق الكامل من أرقام الهواتف العراقية
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

# التعبير النمطي الشامل للرقم العراقي:
# يدعم: 07XXXXXXXXX (11 رقم) أو 7XXXXXXXXX (10 أرقام) أو +9647XXXXXXXXX أو 009647XXXXXXXXX أو 9647XXXXXXXXX
IRAQI_PHONE_REGEX = r'^(?:(?:\+|00)?964|0)?7[3-9]\d{8}$'

iraqi_phone_validator = RegexValidator(
    regex=IRAQI_PHONE_REGEX,
    message=_('يرجى إدخال رقم هاتف عراقي صحيح يبدأ بـ 07 (مثال: 07701234567 أو 07801234567 أو +9647501234567)'),
    code='invalid_iraqi_phone'
)


def clean_phone_digits(value):
    """تنظيف الرقم من الفراغات والشرطات والأقواس"""
    if not value:
        return ''
    return re.sub(r'[\s\-\(\)\.]', '', str(value).strip())


def validate_iraqi_phone(value):
    """
    التحقق الصارم من أن الرقم هو رقم هاتف محمول عراقي صحيح
    يرفض أي رقم لا يطابق مشغلي الاتصالات في العراق (آسيا سيل، زين العراق، كورك، إلخ)
    """
    if not value:
        return value

    cleaned = clean_phone_digits(value)

    if not re.match(IRAQI_PHONE_REGEX, cleaned):
        raise ValidationError(
            _('رقم الهاتف غير صحيح! يجب إدخال رقم هاتف عراقي معتمد يبدأ بـ 07 (مثال: 07701234567 أو 07801234567 أو 07501234567).'),
            code='invalid_iraqi_phone'
        )
    return cleaned


def normalize_iraqi_phone(value, output_format='local'):
    """
    تحويل أي صيغة لرقم الهاتف العراقي إلى الصيغة الموحدة:
    - 'local': 07XXXXXXXXX (11 خانة للاستخدام المحلي والعرض)
    - 'international': +9647XXXXXXXXX (للرسائل الدولية)
    - 'digits': 9647XXXXXXXXX (لروابط الواتساب wa.me)
    """
    if not value:
        return ''

    cleaned = clean_phone_digits(value)
    match = re.match(IRAQI_PHONE_REGEX, cleaned)
    if not match:
        return cleaned

    # استخراج الـ 10 أرقام الأساسية التي تبدأ بـ 7
    if cleaned.startswith('+964'):
        core = cleaned[4:]
    elif cleaned.startswith('00964'):
        core = cleaned[5:]
    elif cleaned.startswith('964'):
        core = cleaned[3:]
    elif cleaned.startswith('0'):
        core = cleaned[1:]
    else:
        core = cleaned

    if output_format == 'local':
        return f"0{core}"
    elif output_format == 'international':
        return f"+964{core}"
    elif output_format == 'digits':
        return f"964{core}"
    return f"0{core}"
