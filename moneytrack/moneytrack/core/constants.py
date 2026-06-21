from django.db import models

class TransactionType(models.TextChoices):
    INCOME = 'INCOME', 'Income'
    EXPENSE = 'EXPENSE', 'Expense'
    
INCOME = 'Income'
EXPENSE = 'Expense'