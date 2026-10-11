"""
Professional Security Captcha Engine - محرك الكابتشا الأمني الاحترافي
حماية من الروبوتات بتصميم حديث SVG وتشفير رقمي آمن
منصة خدماتي
"""
import random
import uuid
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

# الحروف والأرقام المختارة بعناية لمنع الالتباس (استبعاد 0, O, 1, I, l)
CAPTCHA_CHARACTERS = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
CAPTCHA_SALT = 'ail_services_secure_captcha_2026'
CAPTCHA_EXPIRATION_SECONDS = 300  # 5 دقائق


def generate_captcha_text(length=5):
    """توليد كود نصي عشوائي"""
    return ''.join(random.choices(CAPTCHA_CHARACTERS, k=length))


def generate_captcha_svg(code):
    """
    توليد صورة SVG احترافية فائقة الدقة والجمال للكود
    تتضمن خطوط تمويهية، تشويش خلفية، وميول هندسية للأحرف
    """
    width = 190
    height = 60
    
    # ألوان ديناميكية عصرية
    colors = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#06b6d4', '#ec4899', '#14b8a6']
    
    svg_elements = []
    
    # 1. خلفية متدرجة أنيقة
    bg_color1 = "#f8fafc"
    bg_color2 = "#e2e8f0"
    svg_elements.append(
        f'<defs>'
        f'<linearGradient id="captchaBg" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{bg_color1}" />'
        f'<stop offset="100%" stop-color="{bg_color2}" />'
        f'</linearGradient>'
        f'</defs>'
        f'<rect width="{width}" height="{height}" rx="10" fill="url(#captchaBg)" stroke="#cbd5e1" stroke-width="1.5"/>'
    )
    
    # 2. نقاط تشويش خلفية (Noise Dots)
    for _ in range(45):
        cx = random.randint(5, width - 5)
        cy = random.randint(5, height - 5)
        r = random.uniform(1.0, 2.5)
        opacity = random.uniform(0.15, 0.4)
        c = random.choice(colors)
        svg_elements.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="{c}" opacity="{opacity:.2f}"/>')
    
    # 3. خطوط أمان متموجة (Curved Security Lines)
    for _ in range(3):
        x1 = random.randint(5, 30)
        y1 = random.randint(10, height - 10)
        cx1 = random.randint(40, 90)
        cy1 = random.randint(5, height - 5)
        cx2 = random.randint(100, 150)
        cy2 = random.randint(5, height - 5)
        x2 = random.randint(160, width - 5)
        y2 = random.randint(10, height - 10)
        line_color = random.choice(colors)
        stroke_w = random.uniform(1.5, 2.5)
        opacity = random.uniform(0.35, 0.6)
        svg_elements.append(
            f'<path d="M {x1} {y1} C {cx1} {cy1}, {cx2} {cy2}, {x2} {y2}" '
            f'stroke="{line_color}" stroke-width="{stroke_w:.1f}" fill="none" opacity="{opacity:.2f}"/>'
        )
    
    # 4. رسم أحرف الكود مع زوايا دوران عشوائية
    char_spacing = (width - 30) / len(code)
    for i, char in enumerate(code):
        x = 20 + (i * char_spacing) + random.randint(-2, 3)
        y = random.randint(38, 44)
        rot = random.randint(-18, 18)
        char_color = random.choice(colors)
        font_size = random.randint(26, 32)
        font_weight = random.choice(['bold', '700', '800'])
        
        svg_elements.append(
            f'<text x="{x:.1f}" y="{y}" fill="{char_color}" '
            f'font-family="system-ui, -apple-system, sans-serif" font-size="{font_size}px" font-weight="{font_weight}" '
            f'transform="rotate({rot} {x:.1f} {y})">{char}</text>'
        )

    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="user-select:none; border-radius:10px;">{"".join(svg_elements)}</svg>'
    return svg_content


def generate_captcha_challenge():
    """
    توليد تحدي كابتشا كامل مع التوقيع المشفر
    """
    code = generate_captcha_text(5)
    challenge_id = uuid.uuid4().hex[:12]
    
    signer = TimestampSigner(salt=CAPTCHA_SALT)
    # التوقيع المشفر يحتوي على الكود ومعرف التحدي
    signed_token = signer.sign(f"{code}:{challenge_id}")
    svg_html = generate_captcha_svg(code)
    
    return {
        'token': signed_token,
        'svg': svg_html,
        'code': code,  # للاستخدام الداخلي
    }


def verify_captcha_response(signed_token, user_answer):
    """
    التحقق الصارم من صحة الكابتشا:
    - فك التوقيع الرقمي والتحقق من عدم تلاعبه
    - فحص انتهاء الصلاحية الزمنية (أقصى حد 5 دقائق)
    - مقارنة الكود المدخل مع الكود المشفر (دون حساسية لحالة الأحرف)
    """
    if not signed_token or not user_answer:
        return False, "يرجى حل اختبار التحقق الأمني (الكابتشا)."

    signer = TimestampSigner(salt=CAPTCHA_SALT)
    try:
        original_data = signer.unsign(signed_token, max_age=CAPTCHA_EXPIRATION_SECONDS)
        expected_code, _ = original_data.split(':', 1)
        
        clean_user_answer = str(user_answer).strip().upper()
        if clean_user_answer == expected_code.upper():
            return True, "تم التحقق الأمني بنجاح."
        else:
            return False, "رمز التحقق (Captcha) غير صحيح! يرجى إعادة إدخال الرمز الظاهر في الصورة."
    except SignatureExpired:
        return False, "انتهت صلاحية رمز التحقق. يرجى الضغط على زر التحديث للحصول على كود جديد."
    except (BadSignature, ValueError):
        return False, "رمز التحقق غير صالح أو تم التلاعب به."
