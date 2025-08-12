from django.db import models


class PayInterests(models.Model):
    created = models.DateTimeField('Создана', auto_now_add=True)
    loan = models.ForeignKey('loans.Loan', models.CASCADE, verbose_name='Займ')
    amount = models.DecimalField('Сумма', max_digits=7, decimal_places=0)
    is_export = models.BooleanField('Выгружать', default=True, help_text='Без галочки: не отправлять данные в 1С')
    comment = models.CharField('Комментарий', max_length=1024, blank=True)

    def save(self, *args, **kwargs):
        pass

    def __str__(self):
        return f'{self.pk}'

    class Meta:
        managed = False
        db_table = 'operations_payinterests'
        verbose_name = 'Погашенные проценты'
        verbose_name_plural = 'Погашенные проценты'


class PayBody(models.Model):
    created = models.DateTimeField('Создана', auto_now_add=True)
    loan = models.ForeignKey('loans.Loan', models.CASCADE, verbose_name='Займ')
    amount = models.DecimalField('Сумма', max_digits=7, decimal_places=0)
    is_export = models.BooleanField('Выгружать"', default=True, help_text='Не отправлять данные в 1С')
    comment = models.CharField('Комментарий', max_length=1024, blank=True)

    def save(self, *args, **kwargs):
        pass

    def __str__(self):
        return f'{self.pk}'

    class Meta:
        managed = False
        db_table = 'operations_paybody'
        verbose_name = 'Погашенное тело'
        verbose_name_plural = 'Погашенное тело'


class BodyIssue(models.Model):
    """
    Перечисление денег по займу на карту
    """
    BANK_CARD = 'BANK_CARD'
    SBP = 'SBP'
    METHOD_CHOICES = {
        BANK_CARD: 'Банковская карта',
        SBP: 'СБП'
    }

    created = models.DateTimeField('Создана', auto_now_add=True)
    loan = models.ForeignKey('loans.Loan', on_delete=models.CASCADE, verbose_name='Займ')
    bank_card_id = models.PositiveIntegerField('Банковская карта', help_text='Карта для займа', null=True, blank=True)
    amount = models.DecimalField('Сумма', max_digits=7, decimal_places=0, null=True)
    payment_id = models.CharField('TransactionId', help_text='Если заполнено, значит деньги отправлены', max_length=64)
    is_export = models.BooleanField('Выгружать"', default=True, help_text='Не отправлять данные в 1С')
    method = models.CharField('Метод выплаты/оплаты', max_length=16, choices=sorted(METHOD_CHOICES.items()),
                              default=BANK_CARD)
    sbp_member = models.CharField(max_length=32, blank=True, help_text='идентификатор банка при отправке через СБП')
    comment = models.CharField(max_length=1024, blank=True)

    def save(self, *args, **kwargs):
        pass

    def __str__(self):
        return f'{self.pk}'

    class Meta:
        managed = False
        db_table = 'operations_bodyissue'
        verbose_name = 'Выдача займа'
        verbose_name_plural = 'Выдача займа'


class ChargedInterests(models.Model):
    created = models.DateTimeField('Создана', auto_now_add=True)
    loan = models.ForeignKey('loans.Loan', models.CASCADE, verbose_name='Займ')
    amount = models.DecimalField('Сумма', max_digits=7, decimal_places=0, null=True)
    is_export = models.BooleanField('Выгружать"', default=True, help_text='Не отправлять данные в 1С')
    comment = models.CharField('Комментарий', max_length=1024, blank=True)

    def save(self, *args, **kwargs):
        pass

    def __str__(self):
        return f'{self.pk}'

    class Meta:
        managed = False
        db_table = 'operations_chargedinterests'
        verbose_name = 'Начислен проценты'
        verbose_name_plural = 'Начислен проценты'

