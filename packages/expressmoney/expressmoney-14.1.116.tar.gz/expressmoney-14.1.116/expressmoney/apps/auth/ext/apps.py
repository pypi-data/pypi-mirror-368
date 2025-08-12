from django.apps import AppConfig


class ExtConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expressmoney.apps.auth.ext'
    verbose_name = 'Доп. данные'
