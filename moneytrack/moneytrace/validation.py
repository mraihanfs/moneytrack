from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_transaction_type(value):
    if value is not ('D' or 'C'):
        raise ValidationError(_('Transaction type must be either "D" or "C"'))
    
def validate_is_number(value):
    if not value.isdigit():
        raise ValidationError(_('Transaction amount must be a number'))