from django.http import HttpResponse, JsonResponse
from .models import Category, Transaction
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
from .serializers import MyTokenObtainPairSerializer, TransactionSerializer
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
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        dataTransaction = Transaction.objects.select_related('category').order_by('created_at').filter(created_at__date=timezone.now().date())
        dataJson = []
        for d in dataTransaction:
            dataJson.append({'transactionDate': d.created_at.strftime("%d %B %Y"), 'description': d.description,
                            'category': d.category.name, 'amount': d.amount})
        print(request.user)
        return JsonResponse(dataJson, safe=False)

    def post(self, req):
        
        try:
            print(f"Data yang diterima {req.data}")
            serializer = TransactionSerializer(data=req.data)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse(serializer.instance.__str__)
            return Response(serializer.errors, status=400)
        except Exception as e:
            print (f"Data gagal di save dengan error {e}")
            return HttpResponse(f"Data gagal di save dengan error {e}")
        
        
class CategoryView(APIView):
    def get(self, request):
        data = Category.objects.values_list().order_by('name').filter(is_active=True)
        dataJson = []
        for d in data:
            dataJson.append({'id': d[0], 'name': d[3]})
        return JsonResponse(dataJson, safe=False)
        
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