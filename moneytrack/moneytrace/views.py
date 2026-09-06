import logging
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
from .models import Category, Transaction
from django.views.decorators.http import require_http_methods
from django.views import View, generic
from .validation import validate_transaction_type, validate_is_number
from django.contrib.auth import authenticate,  logout
from django.contrib.sessions.models import Session
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .core.permission import HasApiKeyWithName
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RequestTransactionSerializer, ResponseTransactionSerializer
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

# Create your views here.



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
    permission_classes = [HasApiKeyWithName]

    def get(self, request):
        name = request.api_key_name
        logger.info(f"Data params we received is {request.query_params.get('dataRange')}")
        dataRange = request.query_params.get('dataRange')
        if dataRange is None or dataRange == "":
            logger.warning("Query param 'dataRange' is missing or empty")
            return JsonResponse({"message": "Please input a valid query param"}, status=400)
        dataTransaction = None
        if dataRange is not None and dataRange != "":
            match (dataRange.lower()):
                case 'today':
                    dataTransaction = ResponseTransactionSerializer(Transaction.objects.filter(user=name, created_at__date=timezone.now().date()).order_by('-created_at'), many=True).data
                case 'weekly':
                    dataTransaction = ResponseTransactionSerializer(Transaction.objects.filter(user=name, created_at__date__gte=timezone.now().date() - timedelta(days=7)).order_by('-created_at'), many=True).data
                case 'monthly':
                    dataTransaction = ResponseTransactionSerializer(Transaction.objects.filter(user=name, created_at__date__gte=timezone.now().date() - timedelta(days=30)).order_by('-created_at'), many=True).data
                case 'all':
                    dataTransaction = ResponseTransactionSerializer(Transaction.objects.filter(user=name).order_by('-created_at'), many=True).data
                case _:
                    return JsonResponse({"message": "Please input a valid data range"}, status=400)
        if dataTransaction != None and dataTransaction != "":
            return JsonResponse(dataTransaction, safe=False, status=200)
        logger.warning(f"Data with name {name} not found")
        return JsonResponse({"message": "Data with this name: " + name + " is not found, Please use another token"}, status=404)

    def post(self, req):
        try:
            name = req.api_key_name
            obj = req.data.copy()
            logger.info(f"Data we received from {req.api_key_name}")
            newdata = {**obj, 'user': name}
            serializer = RequestTransactionSerializer(data=newdata)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({
                    "status": "success",
                    "message": "Transaction created successfully",
                    "id": serializer.instance.id
                }, status=201)
            return Response(serializer.errors, status=400)
        except Exception as e:
            logger.error(f"Data failed to save with error {e}")
            return HttpResponse(f"Data failed to save with error {e}", status=500)


class CategoryView(APIView):
    def get(self, request):
        data = Category.objects.values_list().order_by('name').filter(is_active=True)
        dataJson = []
        for d in data:
            dataJson.append({'id': d[0], 'name': d[3]})
        return JsonResponse(dataJson, safe=False)
        
class Home(APIView):

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer