from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from moneytrack.core.constants import EXPENSE, INCOME
from moneytrack.core.constants import TransactionType
import logging

logger = logging.getLogger(__name__)

def validate_transaction_type(value):
    if value not in [choice[0] for choice in TransactionType.choices]:
        logger.error(f"Invalid transaction type: {value}. Must be either '{EXPENSE}' or '{INCOME}'.")
        raise ValidationError(_('Transaction type must be either "EXPENSE" or "INCOME"'))

def validate_is_number(value):
    if not value.isdigit():
        logger.error(f"Invalid transaction amount: {value}. Must be a number.")
        raise ValidationError(_('Transaction amount must be a number'))