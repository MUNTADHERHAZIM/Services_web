"""
WhatsApp Verification Service - خدمة تأكيد وتفعيل الحسابات عبر الواتساب
منصة خدماتي
"""
import random
import urllib.parse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from core.validators import normalize_iraqi_phone, validate_iraqi_phone


def generate_otp():
    """توليد رمز أمان عشوائي مكون من 6 أرقام"""
    return f"{random.randint(100000, 999999)}"


def create_or_refresh_whatsapp_otp(user):
    """إنشاء أو تجديد رمز تأكيد الواتساب للمستخدم"""
    profile = getattr(user, 'profile', None)
    if not profile:
        from accounts.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)

    otp = generate_otp()
    profile.whatsapp_otp = otp
    profile.whatsapp_otp_created_at = timezone.now()
    profile.save(update_fields=['whatsapp_otp', 'whatsapp_otp_created_at'])
    return otp


def get_whatsapp_verification_message(otp_code, user_name=None):
    """نص رسالة تأكيد الحساب للواتساب"""
    name_str = f" أخي/أختي {user_name}" if user_name else ""
    return (
        f"مرحباً بك{name_str} في منصة خَـدَمَـاتـي! 🌟\n\n"
        f"رمز التحقق وتأكيد حسابك هو:\n"
        f"👉 *{otp_code}*\n\n"
        f"هذا الرمز صالح لمدة 10 دقائق لحماية أمان حسابك. لا تشارك هذا الرمز مع أي شخص."
    )


def get_whatsapp_direct_link(phone_number, otp_code, user_name=None):
    """
    إنشاء رابط واتساب مباشر لإرسال أو فتح الرسالة بنقرة واحدة
    """
    normalized_digits = normalize_iraqi_phone(phone_number, output_format='digits')
    msg = get_whatsapp_verification_message(otp_code, user_name)
    encoded_msg = urllib.parse.quote(msg)
    
    # رابط wa.me المباشر
    if normalized_digits:
        return f"https://wa.me/{normalized_digits}?text={encoded_msg}"
    return f"https://wa.me/?text={encoded_msg}"


def verify_user_whatsapp_otp(user, entered_code):
    """
    التحقق من رمز الأمان المدخل من قبل المستخدم
    """
    profile = getattr(user, 'profile', None)
    if not profile or not profile.whatsapp_otp:
        return False, "لم يتم طلب رمز تأكيد أو الرمز غير موجود. يرجى طلب رمز جديد."

    # التحقق من الصلاحية الزمنية (10 دقائق)
    if profile.whatsapp_otp_created_at:
        expiry_time = profile.whatsapp_otp_created_at + timedelta(minutes=10)
        if timezone.now() > expiry_time:
            return False, "انتهت صلاحية الرمز المدخل (المدة 10 دقائق). يرجى طلب رمز جديد."

    # التحقق من مطابقة الرمز
    clean_entered = str(entered_code).strip()
    if clean_entered == str(profile.whatsapp_otp).strip():
        profile.phone_verified = True
        profile.whatsapp_verified = True
        profile.whatsapp_otp = None  # حرق الرمز بعد الاستخدام
        profile.save(update_fields=['phone_verified', 'whatsapp_verified', 'whatsapp_otp'])
        return True, "تم تأكيد وتفعيل رقم هاتفك عبر الواتساب بنجاح! أصبح حسابك موثقاً."

    return False, "رمز التحقق غير صحيح! يرجى التأكد من الرمز وإعادة المحاولة."
