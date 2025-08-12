from django.apps import AppConfig


class BlackListConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expressmoney.apps.auth.black_list'
    verbose_name = "Черный список"
