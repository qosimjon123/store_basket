from django.apps import AppConfig


class BasketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Basket'

    def ready(self):
        from .consumer import start_consumer
        start_consumer()