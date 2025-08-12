from django.apps import AppConfig


class CacheConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expressmoney.apps.ru_scoring.cache'
    verbose_name = "Кэш"
