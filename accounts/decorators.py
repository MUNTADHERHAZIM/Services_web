"""
Custom decorators for role-based access control
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def customer_required(view_func):
    """Decorator للتأكد من أن المستخدم عميل"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'يجب إكمال الملف الشخصي أولاً')
            return redirect('accounts:profile')
        
        if not request.user.profile.is_customer():
            messages.error(request, 'هذه الصفحة مخصصة للعملاء فقط')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper


def provider_required(view_func):
    """Decorator للتأكد من أن المستخدم مقدم خدمة"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'يجب إكمال الملف الشخصي أولاً')
            return redirect('accounts:profile')
        
        if not request.user.profile.is_provider():
            messages.error(request, 'هذه الصفحة مخصصة لمقدمي الخدمات فقط')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper


def provider_approved_required(view_func):
    """Decorator للتأكد من أن مقدم الخدمة موثق ومعتمد"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'يجب إكمال الملف الشخصي أولاً')
            return redirect('accounts:profile')
        
        if not request.user.profile.is_provider():
            messages.error(request, 'هذه الصفحة مخصصة لمقدمي الخدمات فقط')
            raise PermissionDenied
        
        if not request.user.profile.provider_approved:
            messages.warning(request, 'حسابك قيد المراجعة. سيتم إخطارك عند الموافقة.')
            return redirect('accounts:profile')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator للتأكد من أن المستخدم مدير"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'هذه الصفحة مخصصة للمديرين فقط')
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper
