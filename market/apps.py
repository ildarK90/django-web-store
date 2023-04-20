from django.apps import AppConfig
from django.core.serializers import register_serializer



class MarketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'market'

register_serializer('json-no-uescape', 'selfserializer.json_no_uescape')