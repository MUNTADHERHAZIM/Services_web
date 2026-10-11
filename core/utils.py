from .models import AuditLog

def log_action(user, action_type, description, request=None):
    """
    مساعد لتسجيل نشاطات النظام بسهولة
    """
    ip_address = None
    user_agent = ""
    
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        # إذا لم يتم تمرير مستخدم وكان الطلب يحتوي على مستخدم مسجل الدخول
        if not user and request.user and request.user.is_authenticated:
            user = request.user
            
    return AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action_type=action_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )
