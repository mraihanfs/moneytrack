import uuid
from django.db import models
import datetime
from django.utils import timezone
# Create your models here.


class Transaction (models.Model):
    TRANSACTION_TYPE = (
        ('D', "Debit"),
        ('C', "Credit"),
    )
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        auto_created=True,
        default=uuid.uuid4,
    )
    description = models.TextField()
    transactionDate = models.DateTimeField(
        unique=True,
        default=timezone.now,
        db_column='transaction_date',
        verbose_name='Transaction Date',
    )
    transactionType = models.CharField(
        verbose_name='transaction_type', 
        max_length=1, 
        choices=TRANSACTION_TYPE
    )
    valueDebet = models.FloatField(
        db_column='value_debet', 
        verbose_name='Value Debet',
        default=0,
    )
    valueCredit = models.FloatField(
        db_column='value_credit', 
        verbose_name='Value Credit',
        default=0,
    )
    sum_value = models.FloatField(
        db_column='sum_value', 
        verbose_name='Sum Value',
        default=0,
    )
    def __str__(self) -> str:
        return f'You make transaction on {self.transactionDate} with expense Rp.{self.valueDebet} and income Rp.{self.valueCredit} with your current acct now is Rp.{self.sum_value}'