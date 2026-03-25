from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json

@require_http_methods(["GET"])
def check_username(request):
    """Check if username is available"""
    import re
    username = request.GET.get('username', '').strip()
    
    if not username:
        return JsonResponse({'available': False, 'message': 'يرجى إدخال اسم مستخدم'})
    
    username = username.replace(' ', '')
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return JsonResponse({'available': False, 'message': 'حروف إنجليزية وأرقام فقط'})
    
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'})
    
    exists = User.objects.filter(username__iexact=username).exists()
    
    if exists:
        # Suggest alternatives
        suggestions = []
        for i in range(1, 4):
            alt = f"{username}{i}"
            if not User.objects.filter(username__iexact=alt).exists():
                suggestions.append(alt)
        
        return JsonResponse({
            'available': False, 
            'message': 'اسم المستخدم مستخدم بالفعل',
            'suggestions': suggestions
        })
    
    return JsonResponse({'available': True, 'message': 'اسم المستخدم متاح! ✓'})


@require_http_methods(["GET"])
def check_email(request):
    """Check if email is available"""
    email = request.GET.get('email', '').strip()
    
    if not email:
        return JsonResponse({'available': False, 'message': 'يرجى إدخال البريد الإلكتروني'})
    
    exists = User.objects.filter(email=email).exists()
    
    if exists:
        return JsonResponse({
            'available': False, 
            'message': 'البريد الإلكتروني مسجل بالفعل. هل تريد تسجيل الدخول؟'
        })
    
    return JsonResponse({'available': True, 'message': 'البريد الإلكتروني متاح! ✓'})
