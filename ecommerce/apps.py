from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecommerce'

    def ready(self):
        # Import signals so Django registers them when the app starts.
        # The underscore prefix suppresses the "imported but unused" warning.
        import ecommerce.signals  # noqa: F401