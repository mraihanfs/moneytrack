from django.contrib import admin
from .models import Transaction
from .models import Category
# Register your models here.
def get_every_field(model):
    return [field.name for field in model._meta.fields]

class TransactionAdmin (admin.ModelAdmin):
    list_display = get_every_field(Transaction)
    
class CategoryAdmin (admin.ModelAdmin):
    list_display = get_every_field(Category)

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)