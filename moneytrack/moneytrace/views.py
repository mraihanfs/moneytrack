from django.http import HttpResponse, JsonResponse
from .models import Transaction
from django.views.decorators.http import require_http_methods
from django.views import View, generic
from .validation import validate_transaction_type, validate_is_number
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import Group
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
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


def check_if_account_had_session(user):
    unexpired_sessions = Session.objects.filter(
        expire_date__gte=timezone.now())
    for session in unexpired_sessions:
        if str(user.pk) == session.get_decoded().get('_auth_user_id'):
            return True
    return False


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
        if user is not None:
            if check_if_account_had_session(user):
                response = {
                    "message": "User sedang login",
                    "status": 403,
                }
                return JsonResponse(response, status=403)
            # req.session.set_expiry(1800)
            # login(req, user=user)
            refresh = RefreshToken.for_user(user)
            response = {
                "message": "Berhasil Login",
                "status": 202,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'first_name': user.first_name
            }
            return JsonResponse(response, status=202)
        else:
            response = {
                "message": "Username atau password tidak ditemukan",
                "status": 403,
            }
            return JsonResponse(response, status=403)


class LogoutView(View):
    def get(self, req):
        for session in Session.objects.filter(expire_date__gte=timezone.now()):
            # Clear the contents of each session
            session.delete()
        return HttpResponse(logout(req))


class TransactionView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = Transaction.objects.values_list().order_by('transactionDate')
        dataJson = []
        for d in data:
            dataJson.append({'id': d[0], 'description': d[1], 'transactionDate': d[2].strftime("%d %B %Y"),
                            'transactionType': d[3], 'valueDebet': d[4], 'valueCredit': d[5], 'sum_value': d[6]})
        print(request.user)
        return JsonResponse(dataJson, safe=False)

    def post(self, req):
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
        
class Home(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request.user.first_name)
        content = {'message': 'Hello, World!',
                   'firstName': request.user.first_name}
        return Response(content)
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer