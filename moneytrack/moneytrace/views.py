from django.http import HttpResponse, JsonResponse
from .models import Transaction
from django.views.decorators.http import require_http_methods
from django.views import View, generic
from .validation import validate_transaction_type, validate_is_number
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
import json
# Create your views here.


def debet_or_credit(transactionType, value):
    validate_transaction_type(transactionType)
    validate_is_number(value)
    value = abs(float(value))
    if transactionType == 'D':
        return [0, value]
    elif transactionType == 'C':
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

class LoginView(View):
    def post(self, req):
        username = req.POST.get('username')
        password = req.POST.get('password')
        user = authenticate(req, username=username, password=password)
        if user.is_authenticated:
            return HttpResponse("User sedang login mohon menggunakan akun yang lain", status=403)
        else:
            if user is not None:
                req.session.set_expiry(1800)
                login(req, user=user)
                response = {
                    "status": "202",
                    "message": "Berhasil Login"
                }
                return JsonResponse(response)
            else:
                return HttpResponse("Username atau password salah", status=403)

class LogoutView(View):
    def get(self, req):
        return HttpResponse(logout(req))

class TransactionView(LoginRequiredMixin, View):
    raise_exception = True
    permission_denied_message = "Anda belum login"

    def get(self, request):
        data = Transaction.objects.values_list().order_by('transactionDate')
        dataJson = []
        for d in data:
            dataJson.append({'id': d[0], 'description': d[1], 'transactionDate': d[2].strftime("%d %B %Y"),
                            'transactionType': d[3], 'valueDebet': d[4], 'valueCredit': d[5], 'sum_value': d[6]})
        print(request.user)
        return JsonResponse(dataJson, safe=False)
    
    def post (self, req):
        data = req.POST
        try:
            description = str(data['description'])
            transactionType = str(data['transactionType'])
            value = data['value']
            value = debet_or_credit(transactionType, value)
            sum_value = sum_of_transaction(value[0], value[1])    
            newTransaction = Transaction(description=description, transactionType=transactionType,
                                        valueCredit=value[0], valueDebet=value[1], sum_value=sum_value)
            newTransaction.save()
            return HttpResponse(newTransaction.__str__)
        except Exception as e:
            return HttpResponse(f"Data gagal di save dengan error {e}")
