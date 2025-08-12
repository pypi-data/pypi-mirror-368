from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class Department(models.Model):
    created = models.DateTimeField('Создано', auto_now_add=True)
    updated = models.DateTimeField('Изменено', auto_now=True)
    name = models.CharField('Название', max_length=64, unique=True)
    comment = models.CharField('Комментарий', max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'


class Ext(models.Model):
    created = models.DateTimeField('Создано', auto_now_add=True)
    updated = models.DateTimeField('Изменено', auto_now=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                verbose_name='Пользователь', primary_key=True)
    phonenumber = PhoneNumberField(unique=True, verbose_name='Номер телефона')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='Подразделение')
    ip = models.GenericIPAddressField()
    http_referer = models.URLField('Реф. ссылка', blank=True, max_length=2048)

    def set_department(self, department_id):
        self.department_id = department_id
        super().save()

    def __str__(self):
        return f'{self.user_id}'

    class Meta:
        managed = False
        verbose_name = 'Расширение пользователя'
        verbose_name_plural = 'Расширение пользователей'
