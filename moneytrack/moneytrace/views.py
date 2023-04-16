from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Transaction
from django.views.decorators.http import require_http_methods
from django.views import generic
from django.template.context_processors import csrf
from django.utils import timezone
import uuid

# Create your views here.


def debet_or_credit(transactionType, value):
    if transactionType == 'D':
        return [0, value]
    return [value, 0]


def sum_of_transaction(valueCredit, valueDebet):
    sumOfTransaction = valueCredit - valueDebet
    try:
        sum_value = Transaction.objects.latest('transactionDate').sum_value
        sumOfTransaction = sum_value + sumOfTransaction
    finally:
        return sumOfTransaction


def get_every_field(model):
    return [field.name for field in model._meta.fields]


@require_http_methods(['GET'])
class IndexView (generic.ListView):
    context_object_name = 'latest_transasction'
    model = Transaction

    def get_queryset(self):
        return Transaction.objects.order_by('transaction_date')[-5]

@require_http_methods(['POST', 'GET'])
def add_transaction_and_show(req):
    if req.method == 'GET':
        data = Transaction.objects.values_list().order_by('transactionDate')
        dataJson = []
        for d in data:
            dataJson.append({'id': d[0], 'description': d[1], 'transactionDate': d[2].strftime("%d %B %Y"),
                            'transactionType': d[3], 'valueDebet': d[4], 'valueCredit': d[5], 'sum_value': d[6]})
        return JsonResponse(dataJson, safe=False)
    elif req.method == "POST":
        data = req.POST
        id = uuid.uuid4
        description = str(data['description'])
        transactionType = str(data['transactionType'])
        value = float(data['value'])
        value = debet_or_credit(transactionType, value)
        sum_value = sum_of_transaction(value[0], value[1])
        try:
            newTransaction = Transaction(description=description, transactionType=transactionType,
                                        valueCredit=value[0], valueDebet=value[1], sum_value=sum_value)
            newTransaction.save()
            return HttpResponse(newTransaction.__str__)
        except Exception as e:
            return HttpResponse(f"Data gagal di save dengan error {e}")
