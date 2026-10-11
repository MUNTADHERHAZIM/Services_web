from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "إدارة الحسابات والمستخدمين"

    def ready(self):
        from django.contrib.auth.apps import AuthConfig
        AuthConfig.verbose_name = "الصلاحيات ومجموعات العمل"
