from django.db import models


class NBKICreditHistoryV2(models.Model):
    """
    from cache.models import NBKICreditHistoryV2
    """
    created = models.DateTimeField(auto_now_add=True)
    xml = models.URLField(blank=True, help_text='Ссылка на текущую КИ в формате xml')
    time = models.DecimalField(max_digits=9, decimal_places=4, null=True, help_text='Время загрузки КИ')
    # Personal data
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32)
    birth_date = models.DateField()
    passport_serial = models.CharField(max_length=4)
    passport_number = models.CharField(max_length=6)
    passport_date = models.DateField()
    passport_code = models.CharField(max_length=7, blank=True)
    snils = models.CharField(max_length=64, blank=True)
    # NBKI features
    accounts_total_mfo_3y = models.IntegerField(null=True, help_text='Всего счетов МФО за 3 года')
    accounts_total_mfo_gt3y = models.IntegerField(null=True, help_text='Всего счетов МФО от 3 лет')
    accounts_total_bank_3y = models.IntegerField(null=True, help_text='Всего счетов БАНК за 3 года')
    accounts_total_bank_gt3y = models.IntegerField(null=True, help_text='Всего счетов БАНК от 3 лет')
    accounts_active_mfo = models.IntegerField(null=True, help_text='Действующих счетов МФО')
    accounts_active_bank = models.IntegerField(null=True, help_text='Действующих счетов БАНК')
    accounts_zero = models.IntegerField(null=True, help_text='Действующих счетов без платежей')
    accounts_pastdue_mfo = models.IntegerField(null=True, help_text='Просрочено счетов МФО')
    accounts_pastdue_bank = models.IntegerField(null=True, help_text='Просрочено счетов БАНК')
    accounts_closed_mfo_3y = models.IntegerField(null=True, help_text='Всего закрыто МФО за 3 года')
    accounts_closed_mfo_gt3y = models.IntegerField(null=True, help_text='Всего закрыто МФО от 3 лет')
    accounts_closed_bank_3y = models.IntegerField(null=True, help_text='Всего закрыто БАНК за 3 года')
    accounts_closed_bank_gt3y = models.IntegerField(null=True, help_text='Всего закрыто БАНК от 3 лет')
    balance_credit_mfo_3y = models.IntegerField(null=True, help_text='Выдано тело МФО за 3 года')
    balance_credit_mfo_gt3y = models.IntegerField(null=True, help_text='Выдано тело МФО от 3 лет')
    balance_credit_bank_3y = models.IntegerField(null=True, help_text='Выдано тело БАНК за 3 года')
    balance_credit_bank_gt3y = models.IntegerField(null=True, help_text='Выдано тело БАНК от 3 лет')
    balance_debt_mfo = models.IntegerField(null=True, help_text='Текущий долг по займам МФО')
    balance_debt_bank = models.IntegerField(null=True, help_text='Текущий долг по кредитам БАНК')
    balance_nextpay_mfo = models.IntegerField(null=True, help_text='Следующий платеж по займам МФО')
    balance_nextpay_bank = models.IntegerField(null=True, help_text='Следующий платеж по кредитам БАНК')
    balance_paid_mfo_3y = models.IntegerField(null=True, help_text='Выплачено по займам МФО за 3 года')
    balance_paid_mfo_gt3y = models.IntegerField(null=True, help_text='Выплачено по займам МФО от 3 лет')
    balance_paid_bank_3y = models.IntegerField(null=True, help_text='Выплачено по кредитам БАНК за 3 года')
    balance_paid_bank_gt3y = models.IntegerField(null=True, help_text='Выплачено по кредитам БАНК от 3 лет')
    balance_pastdue_mfo = models.IntegerField(null=True, help_text='Текущая просрочка по займам МФО')
    balance_pastdue_bank = models.IntegerField(null=True, help_text='Текущая просрочка по кредитам БАНК')
    inquiries_total = models.IntegerField(null=True, help_text='Всего запросов на получение займов и кредитов')
    inquiries_amount_mfo = models.IntegerField(null=True, help_text='Средняя запрашиваемая сумма в МФО')
    inquiries_amount_bank = models.IntegerField(null=True, help_text='Средняя запрашиваемая сумма в Банке')
    inquiries_7 = models.IntegerField(null=True, help_text='Запросы за последние 7 дней')
    inquiries_14 = models.IntegerField(null=True, help_text='Запросы за последние 14 дней')
    inquiries_21 = models.IntegerField(null=True, help_text='Запросы за последние 21 дней')
    inquiries_30 = models.IntegerField(null=True, help_text='Запросы за последние 30 дней')
    inquiries_60 = models.IntegerField(null=True, help_text='Запросы за последние 60 дней')
    inquiries_90 = models.IntegerField(null=True, help_text='Запросы за последние 90 дней')
    inquiries_180 = models.IntegerField(null=True, help_text='Запросы за последние 180 дней')
    inquiries_365 = models.IntegerField(null=True, help_text='Запросы за последние 365 дней')
    rate_inquiries = models.DecimalField(max_digits=3, decimal_places=2, null=True, help_text='Счета/Запросы')
    rate_inquiries_7 = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                           help_text='Всего счетов за 3г к запросам за 7 дней')
    rate_inquiries_7_365 = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                               help_text='Всего запросов к запросам за 7 дней')
    rate_inquiries_14 = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                            help_text='Всего счетов за 3г к запросам за 14 дней')
    rate_inquiries_14_365 = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                                help_text='Всего запросов к запросам за 14 дней')
    rate_closed = models.DecimalField(max_digits=3, decimal_places=2, null=True, help_text='Закрыто сч./Всего счетов')
    rate_paid = models.DecimalField(max_digits=3, decimal_places=2, null=True, help_text='Выплачено / Всего выдано')
    rate_debt = models.DecimalField(max_digits=3, decimal_places=2, null=True, help_text='Долг/выдано')
    rate_pastdue = models.DecimalField(max_digits=3, decimal_places=2, null=True, help_text='Просрочено/Выдано')
    rate_pastdue_debt = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                            help_text='Просроченная задолженность к всего задолженность')
    rate_zero = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                    help_text='Счето без оплат к всего счетов за 3 года')
    rate_zero_active = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                           help_text='Счето без оплат к активным')
    rate_active = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                      help_text='Активных к всего счетов за 3 года')
    rate_accounts_pastdue = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                                help_text='Просроченных к всего счетам за 3 года')
    rate_accounts_pastdue_active = models.DecimalField(max_digits=3, decimal_places=2, null=True,
                                                       help_text='Просроченных к активным счетам за 3 года')
    avg_credit_mfo_3y = models.IntegerField(null=True, help_text='Средняя сумма займа за последние 3 года')
    avg_credit_bank_3y = models.IntegerField(null=True, help_text='Средняя сумма кредита за последние 3 года')
    max_credit_amount_mfo_3y = models.IntegerField(null=True, help_text='Максимальная сумма займа/кредита')
    max_credit_amount_mfo_gt3y = models.IntegerField(null=True, help_text='Максимальная сумма займа/кредита')
    max_credit_amount_bank_3y = models.IntegerField(null=True, help_text='Максимальная сумма займа/кредита')
    max_credit_amount_bank_gt3y = models.IntegerField(null=True, help_text='Максимальная сумма займа/кредита')
    interests_mfo_3y = models.IntegerField(null=True, help_text='Выплачено процентов по закрытым счетам')
    interests_mfo_gt3y = models.IntegerField(null=True, help_text='Выплачено процентов по закрытым счетам')
    interests_bank_3y = models.IntegerField(null=True, help_text='Выплачено процентов по закрытым счетам')
    interests_bank_gt3y = models.IntegerField(null=True, help_text='Выплачено процентов по закрытым счетам')
    interests_avg_mfo_3y = models.IntegerField(null=True, help_text='В среднем выплачено процентов на 1 займ/кредит')
    interests_avg_mfo_gt3y = models.IntegerField(null=True, help_text='В среднем выплачено процентов на 1 займ/кредит')
    interests_avg_bank_3y = models.IntegerField(null=True, help_text='В среднем выплачено процентов на 1 займ/кредит')
    interests_avg_bank_gt3y = models.IntegerField(null=True, help_text='В среднем выплачено процентов на 1 займ/кредит')
    days_last = models.IntegerField(null=True, help_text='Дней с последнего займа/кредита')
    days_between = models.IntegerField(null=True, help_text='Дней между займами/кредитами')

    def save(self, *args, **kwargs):
        pass

    def __str__(self):
        return str(self.pk)

    class Meta:
        managed = False
        verbose_name_plural = 'NBKI credit history v2'
        ordering = ('-created',)


class NBKIScore(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    score = models.PositiveSmallIntegerField()
    # Passport
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32)
    birth_date = models.DateField()
    passport_serial = models.CharField(max_length=4)
    passport_number = models.CharField(max_length=6)
    passport_date = models.DateField()
    passport_code = models.CharField(max_length=7, blank=True)
    snils = models.CharField(max_length=64, blank=True)

    def save(self, *args, **kwargs):
        pass

    def __str__(self):
        return str(self.pk)

    class Meta:
        managed = False
