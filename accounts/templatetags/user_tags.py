"""
Custom template tags for user role checking
"""

from django import template

register = template.Library()


@register.simple_tag
def is_customer(user):
    """هل المستخدم عميل؟"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'profile') and user.profile.is_customer()


@register.simple_tag
def is_provider(user):
    """هل المستخدم مقدم خدمة؟"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'profile') and user.profile.is_provider()


@register.simple_tag
def is_admin(user):
    """هل المستخدم مدير؟"""
    if not user.is_authenticated:
        return False
    return user.is_staff or (hasattr(user, 'profile') and user.profile.is_admin())


@register.simple_tag
def can_create_services(user):
    """هل يمكن للمستخدم إنشاء خدمات؟"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'profile') and user.profile.can_create_services()


@register.simple_tag
def is_provider_approved(user):
    """هل مقدم الخدمة معتمد؟"""
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'profile'):
        return False
    return user.profile.is_provider() and user.profile.provider_approved


@register.filter
def user_type_badge(user):
    """إرجاع badge HTML حسب نوع المستخدم"""
    if not hasattr(user, 'profile'):
        return ''
    
    if user.profile.is_admin():
        return '<span class="badge bg-danger"><i class="bi bi-shield-fill-check me-1"></i>مدير</span>'
    elif user.profile.is_provider():
        if user.profile.provider_approved:
            return '<span class="badge bg-success"><i class="bi bi-patch-check-fill me-1"></i>مقدم خدمة موثق</span>'
        else:
            return '<span class="badge bg-warning"><i class="bi bi-clock-fill me-1"></i>مقدم خدمة (قيد المراجعة)</span>'
    elif user.profile.is_customer():
        return '<span class="badge bg-primary"><i class="bi bi-person-fill me-1"></i>عميل</span>'
    
    return ''
