from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .utils import log_action

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_action(user, 'login', f"تسجيل دخول ناجح للمستخدم '{user.username}'", request)

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        log_action(user, 'logout', f"تسجيل خروج للمستخدم '{user.username}'", request)

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'غير معروف')
    log_action(None, 'failed_login', f"محاولة تسجيل دخول فاشلة للمستخدم '{username}'", request)
