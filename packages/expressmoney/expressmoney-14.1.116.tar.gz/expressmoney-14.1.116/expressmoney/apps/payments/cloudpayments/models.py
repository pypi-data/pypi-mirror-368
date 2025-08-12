from django.db import models


class BankCard(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user_id = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    bin = models.CharField(max_length=6)
    number = models.CharField(max_length=4, help_text='Последние 4 цифры номера карты')
    card_number = models.CharField('Номер карты', max_length=19, blank=True)
    expiry_month = models.PositiveSmallIntegerField()
    expiry_year = models.PositiveSmallIntegerField()
    ip = models.GenericIPAddressField(blank=True, null=True)
    token = models.CharField(max_length=1024, unique=True)
    comment = models.TextField(max_length=512, blank=True, help_text='Причина перевода в статус неактивной')
    # Справочная информация о карте
    brand = models.CharField('Марка', max_length=64, blank=True)
    type = models.CharField('Тип', max_length=24, blank=True)
    category = models.CharField('Категория', max_length=64, blank=True)
    issuer = models.CharField('Банк', max_length=128, blank=True)
    issuer_phone = models.CharField('Номер телефона банка', max_length=128, blank=True)
    issuer_url = models.URLField('Сайт банка', max_length=128, blank=True)
    iso_code2 = models.CharField('Страна', max_length=24, help_text='по стандарту ISO 3166-1 alpha-2', blank=True)
    iso_code3 = models.CharField('Страна', max_length=24, help_text='по стандарту ISO 3166-1 alpha-3', blank=True)
    country_name = models.CharField('Страна полное название', max_length=64, blank=True)

    def __str__(self):
        number = self.card_number
        return f'{number[:4]} {number[4:8]} {number[8:12]} {number[12:16]} {number[16:20]}'

    class Meta:
        managed = False
        verbose_name_plural = 'Банковские карты'
        verbose_name = 'Банковская карта'
        unique_together = ('bin', 'number', 'expiry_month', 'expiry_year')
        constraints = (
            models.UniqueConstraint(fields=['bin', 'number', 'expiry_month', 'expiry_year'], name='unique_bank_card'),
        )
