from decimal import Decimal

from django.db import models


class Loan(models.Model):
    ISSUING = 'ISSUING'
    OPEN = "OPEN"  # Клиент получил деньги
    OVERDUE = "OVERDUE"
    STOP_INTEREST = "STOP_INTEREST"
    CLOSED = "CLOSED"
    CANCELED = 'CANCELED'
    STATUS_CHOICES = {
        ISSUING: 'Выдается',
        OPEN: "Открыт",
        OVERDUE: "Просрочен",
        STOP_INTEREST: "Остановлена проценты",
        CLOSED: "Закрыт",
        CANCELED: 'Отменен',
    }

    BANK_CARD = 'BANK_CARD'
    SBP = 'SBP'
    METHOD_CHOICES = {
        BANK_CARD: 'Банковская карта',
        SBP: 'СБП'
    }

    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Изменен', auto_now=True)
    order = models.OneToOneField('orders.Order', on_delete=models.PROTECT, verbose_name='Заявка')
    extended_start_date = models.DateField('Начало пролонгации', null=True)
    extended_end_date = models.DateField('Окончание пролонгации', null=True)
    bank_card_id = models.PositiveIntegerField('Банковская карта', null=True, help_text='Карта для зачисления займа')
    interests_charged_date = models.DateField('Проценты начислены', null=True, help_text='Дата последнего начисления')
    status = models.CharField('Статус', max_length=16, choices=sorted(STATUS_CHOICES.items()), default=ISSUING)
    expiry_date = models.DateField('Дата окончания', help_text='По договору без учета пролонгации')
    closed_date = models.DateTimeField('Дата закрытия', null=True, help_text='Дата фактического закрытия')
    sign = models.PositiveSmallIntegerField('Подпись')
    ip = models.GenericIPAddressField()
    document = models.FileField('Договор', upload_to="files/", blank=True, help_text='Печатный договор займа')
    comment = models.CharField('Комментарий', max_length=2048, blank=True)

    interest_rate = models.DecimalField('Процентная ставка', max_digits=3, decimal_places=2)
    period = models.PositiveSmallIntegerField('Срок в днях')
    free_period = models.PositiveSmallIntegerField('Беспроцентный период')

    body_issue = models.DecimalField('Выдано тело', max_digits=7, decimal_places=0, default=Decimal(0))
    interests_charged = models.DecimalField('Начислено процентов', max_digits=7, decimal_places=0, default=Decimal(0))
    interests_paid = models.DecimalField('Выплачено процентов', max_digits=7, decimal_places=0, default=Decimal(0))
    body_paid = models.DecimalField('Выплачено тело', max_digits=7, decimal_places=0, default=Decimal(0))
    method = models.CharField('Метод выплаты/оплаты', max_length=16, choices=sorted(METHOD_CHOICES.items()),
                              default=BANK_CARD)

    @property
    def interests_balance(self):
        """Долг по процентам"""
        return self.interests_charged - self.interests_paid

    @property
    def body_balance(self):
        """Долг по телу"""
        return self.body_issue - self.body_paid

    @property
    def balance(self):
        """Общий долг"""
        return self.interests_balance + self.body_balance

    def save(self, *args, **kwargs):
        pass

    def __str__(self):
        return f'{self.pk}'

    class Meta:
        managed = False
        verbose_name_plural = 'Займы'
        verbose_name = 'Займ'
