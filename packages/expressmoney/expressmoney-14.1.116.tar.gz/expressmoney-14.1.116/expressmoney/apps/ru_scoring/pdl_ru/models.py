from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models

from expressmoney.apps.ru_scoring.cache.models import NBKIScore, NBKICreditHistoryV2


class Scoring(models.Model):
    """
    from pdl_ru.models import Scoring
    obj = Scoring.objects.create(**{
        "amount_requested": 16_000,
        "period_requested": 30,
        "first_name": "Султан",
        "last_name": "Шамурзаев",
        "middle_name": "Хазретович",
        "birth_date": "1999-08-22",
        "passport_serial": "9019",
        "passport_number": "314603",
        "passport_code": "150-010",
        "passport_date": "2019-09-25",
        "snils": "15460066042",
        "total_loans": 0,
        "interests_sum": 0,
        "body_sum": 0,
        "body_max": 0,
        "department": "zaem.ru"
    })
    """

    created = models.DateTimeField(auto_now_add=True)
    # Order
    order_id = models.CharField(max_length=32, unique=True, validators=(MinLengthValidator(1),), null=True)
    user_id = models.PositiveIntegerField(null=True)
    period_requested = models.PositiveSmallIntegerField(validators=(MinValueValidator(1), MaxValueValidator(500)))
    amount_requested = models.PositiveIntegerField(validators=(MinValueValidator(1000), MaxValueValidator(200000)))
    # Passport
    first_name = models.CharField(max_length=32, validators=(MinLengthValidator(1),))
    last_name = models.CharField(max_length=32, validators=(MinLengthValidator(1),))
    middle_name = models.CharField(max_length=32)
    birth_date = models.DateField()
    passport_serial = models.CharField(max_length=4, validators=(MinLengthValidator(4),))
    passport_number = models.CharField(max_length=6, validators=(MinLengthValidator(6),))
    passport_date = models.DateField()
    passport_code = models.CharField(max_length=7, validators=(MinLengthValidator(7),))
    snils = models.CharField(max_length=16)
    # Loans data
    total_loans = models.PositiveIntegerField(help_text='Всего займов')
    interests_sum = models.PositiveIntegerField(help_text='Всего выплачено процентов')
    body_sum = models.PositiveIntegerField(help_text='Всего выплачено тело')
    body_max = models.PositiveIntegerField(help_text='Максимально выданная ранее сумма')
    first_loan = models.IntegerField(null=True, help_text='Дней с первого займа')
    last_loan = models.IntegerField(null=True, help_text='Дней с последнего займа')
    between_loans = models.IntegerField(null=True, help_text='Ср. кол. дней между займами')
    # Data
    score = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    score_min = models.DecimalField(max_digits=3, decimal_places=2, help_text='Мин. скор для одобр. суммы', null=True)
    amount_approved = models.PositiveIntegerField(null=True)
    department = models.CharField(max_length=128, default='', help_text='Бизнес-юнит. Например: займы.рф', null=True)
    cache_ki = models.ForeignKey(NBKICreditHistoryV2,
                                 models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 related_name='%(app_label)s_%(class)s')
    cache_score = models.ForeignKey(NBKIScore,
                                    models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    related_name='%(app_label)s_%(class)s')
    nbki_score = models.PositiveIntegerField(null=True)
    xml = models.CharField(max_length=512, blank=True)
    time = models.DecimalField(max_digits=9, decimal_places=4, null=True, help_text='Время расчета скора, секунды')
    is_black_list = models.BooleanField(null=True)
    is_offline = models.BooleanField(null=True, help_text='Минимум один раз лично посещал офис')
    comment = models.TextField(max_length=1024, blank=True)

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False


class FeatureStore(models.Model):
    order_id = models.CharField(primary_key=True, max_length=32)
    is_from_scoring = models.BooleanField(default=True, help_text='False - это займы примерно до конца мая 2023, '
                                                                  'их нет в Scoring. (71 025  шт.) '
                                                                  'Удалять нельзя так как не восстановить.')
    is_refilled = models.BooleanField(default=True, help_text='True - фичи перезаполнены. Сбросить перед заполнением.')
    revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                  help_text='Сумма выплаченных процентов с момента выдачи займа на момент заполнения')
    ENDPOINT_ID = None
    MODEL_NAME = None
    explanation = None
    last_ki = None
    _max_inquiries_7 = 15
    # Order
    order_created = models.DateTimeField()
    period_requested = models.PositiveSmallIntegerField()
    amount_requested = models.PositiveIntegerField()
    amount_approved = models.PositiveIntegerField()
    # Other
    comment = models.CharField(max_length=1024, default='')
    time = models.DecimalField(max_digits=9, decimal_places=4, null=True, help_text='Время расчета скора, секунды')
    department = models.CharField(max_length=32, blank=True)
    is_offline = models.BooleanField(null=True, help_text='Минимум один раз лично посещал офис')
    # User
    user_id = models.PositiveIntegerField(null=True)
    # Profile
    first_name = models.CharField(max_length=32, default='')
    last_name = models.CharField(max_length=32, default='')
    middle_name = models.CharField(max_length=32, default='')
    birth_date = models.DateField(null=True)
    passport_serial = models.CharField(max_length=4, default='')
    passport_number = models.CharField(max_length=6, default='')
    passport_date = models.DateField(null=True)
    passport_code = models.CharField(max_length=7, blank=True)
    snils = models.CharField(max_length=16, default='')
    # Loan
    loan_id = models.PositiveIntegerField(null=True, unique=True)
    loan_created = models.DateField(null=True)
    loan_status = models.CharField(max_length=16, null=True)
    loan_status_date = models.DateField(null=True)
    # Expressmoney features
    em_total_loans = models.IntegerField(null=True, help_text='Всего займов')
    em_between_loans = models.IntegerField(null=True, help_text='Ср. кол. дней между займами')
    em_first_loan = models.IntegerField(null=True, help_text='Дней с первого займа')
    em_last_loan = models.IntegerField(null=True, help_text='Дней с последнего займа')
    em_interests_sum = models.IntegerField(null=True, help_text='Выплачено процентов по всем предыдущим займам')
    em_interests_mean = models.IntegerField(null=True, help_text='В среднем выплачено процентов на 1 займ')
    em_interests_rate = models.IntegerField(null=True, help_text='Выплачено процентов / Одобренная сумма')
    em_body_sum = models.IntegerField(null=True, help_text='Сумма тела всех займов')
    em_body_mean = models.IntegerField(null=True, help_text='Средняя сумма займа')
    em_body_mean_rate = models.IntegerField(null=True, help_text='Средняя сумма тела / Одобренная сумма')
    em_body_max = models.IntegerField(null=True, help_text='Максимальная сумма займа')
    em_body_max_rate = models.IntegerField(null=True, help_text='Максимальная сумма займа / Одобренная сумма')
    # NBKI score
    nbki_score = models.IntegerField(null=True, help_text='Больше - лучше')
    # NBKI features
    accounts_30d = models.IntegerField(null=True, help_text='Всего счетов МФО за 30 дней')
    accounts_mfo_30d = models.IntegerField(null=True, help_text='Всего счетов МФО за 30 дней')
    accounts_mfo_30d_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True, help_text='Доля МФО 30 дней')
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

    # Source
    xml = models.CharField(max_length=512, default='', help_text='Название xml использованного для заполнения фичей')
    cache_ki = models.ForeignKey(NBKICreditHistoryV2,
                                 models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 related_name='%(app_label)s_%(class)s')
    cache_score = models.ForeignKey(NBKIScore,
                                    models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    related_name='%(app_label)s_%(class)s')

    class Meta:
        managed = False