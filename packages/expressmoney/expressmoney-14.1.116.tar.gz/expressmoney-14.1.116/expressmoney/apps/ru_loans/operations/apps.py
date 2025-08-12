from django.apps import AppConfig


class OperationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'ru_loans_operations'
    name = 'expressmoney.apps.ru_loans.operations'
    verbose_name = 'Операции по займам'
