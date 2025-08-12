from django.db import models


class Device(models.Model):
    created = models.DateTimeField('Создано', auto_now_add=True)
    user_id = models.PositiveIntegerField()
    uuid = models.CharField('UUID', max_length=40, help_text='Уникальный идентификатор устройства')
    ip = models.CharField(max_length=64)
    isp = models.CharField('ISP', max_length=256)
    fingerprint = models.CharField('Fingerprint', max_length=32)
    country = models.CharField('Страна', max_length=4)

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'
