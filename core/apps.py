from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "إعدادات المنصة وسجل الأمان"

    def ready(self):
        import core.signals
        try:
            from django.contrib.admin.models import LogEntry
            LogEntry._meta.verbose_name = "سجل عمليات الإدارة"
            LogEntry._meta.verbose_name_plural = "سجل عمليات الإدارة والتعديلات"
        except Exception:
            pass

