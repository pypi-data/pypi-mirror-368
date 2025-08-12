from django.db import models


class Order(models.Model):
    NEW = 'NEW'
    DECLINED = 'DECLINED'
    LOAN_CREATED = 'LOAN_CREATED'
    EXPIRED = 'EXPIRED'
    STATUS_CHOICES = {
        NEW: 'Новая',
        LOAN_CREATED: 'Займ создан',
        DECLINED: 'Отклонена',
        EXPIRED: 'Истекла',
    }
    created = models.DateTimeField('Создана', auto_now_add=True)
    updated = models.DateTimeField('Изменена', auto_now=True)
    user_id = models.PositiveIntegerField()
    amount_requested = models.DecimalField('Запрошенная сумма', max_digits=7, decimal_places=0)
    amount_approved = models.DecimalField('Одобренная сумма', max_digits=7, decimal_places=0, null=True)
    amount_approved_max = models.DecimalField('Макс. одобренная сумма', max_digits=7, decimal_places=0, null=True)
    period_requested = models.PositiveSmallIntegerField('Запрошенный период')
    period_approved = models.PositiveSmallIntegerField('Одобренный период', blank=True, null=True)
    period_free = models.PositiveSmallIntegerField('Беспроцентный период')
    interests = models.DecimalField('Процентная ставка', max_digits=3, decimal_places=2)
    sign = models.PositiveSmallIntegerField('Подпись')
    attempts = models.PositiveSmallIntegerField('Попытки', default=0, help_text='Попытки ввода подписи')
    status = models.CharField('Статус', max_length=30, choices=sorted(STATUS_CHOICES.items()), default=NEW)
    promocode_code = models.CharField('Промокод', max_length=16, blank=True)
    contract_demo = models.FileField('Демо договора', upload_to="files/", blank=True)
    is_first_loan = models.BooleanField('Первый займ', null=True, blank=True,
                                        help_text='True - ранее у юзера не было займов')
    is_first_order = models.BooleanField('Первая заявка', null=True, blank=True,
                                         help_text='True - ранее у юзера не было заявок')
    weeks_in_period = models.PositiveSmallIntegerField('Недель в периоде', null=True,
                                                       help_text='Для IL. Кол недель в платежном периоде')
    comment = models.CharField('Комментарий', max_length=1024, blank=True)

    def save(self, *args, **kwargs):
        pass

    def __str__(self):
        return f'{self.id}'

    class Meta:
        managed = False
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class OrderIL(Order):
    class Meta:
        proxy = True
        verbose_name = 'Заявка IL'
        verbose_name_plural = 'Заявки IL'


class Schedule(models.Model):
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Изменен', auto_now=True)
    is_paid = models.BooleanField('Оплачен', default=False)
    order = models.ForeignKey('OrderIL', models.PROTECT, verbose_name='Заявка')
    payment_number = models.SmallIntegerField('Номер платежа')
    payment_date = models.DateField('Дата платежа')
    amount_body = models.DecimalField('Платеж по телу', max_digits=7, decimal_places=0)
    amount_interests = models.DecimalField('Платеж по процентам', max_digits=7, decimal_places=0)
    balance_body = models.DecimalField('Остаток по телу', max_digits=7, decimal_places=0)
    balance_interests = models.DecimalField('Остаток по процентам', max_digits=7, decimal_places=0)

    @property
    def payment(self):
        return self.amount_body + self.amount_interests

    @property
    def balance(self):
        return self.balance_body + self.balance_interests

    def save(self, *args, **kwargs):
        pass

    def get_next_schedule(self):
        if not self.__next_schedule:
            self.__next_schedule = self.__class__.objects.filter(order=self.order,
                                                                 payment_number__gt=self.payment_number,
                                                                 ).order_by('payment_number').first()
        return self.__next_schedule

    def __str__(self):
        return f'{self.pk}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__next_schedule = None

    class Meta:
        managed = False
        verbose_name = 'График платежей'
        verbose_name_plural = 'Графики платежей'
