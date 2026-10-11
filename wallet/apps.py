from django.apps import AppConfig


class WalletConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wallet"
    verbose_name = "المحفظة"

    def ready(self):
        import wallet.signals

