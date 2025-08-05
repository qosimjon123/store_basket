from django.apps import AppConfig


class ProductConfig(AppConfig):
    name = 'ProductInfo'

    def ready(self):
        import ProductInfo.signals
        from . import StreamConsumer
        StreamConsumer.start_consumer_pool()
