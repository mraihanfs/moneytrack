from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Transaction, Category

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        groups = self.user.groups.all().values_list('name', flat=True)
        data["groups"] =list(groups)
        
        return data
    
class RequestTransactionSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.filter(is_active=True),
        slug_field='name'
    )
    
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'category', 'user']
        
        
class ResponseTransactionSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.filter(is_active=True),
        slug_field='name'
    )
    
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'category', 'user', 'created_at', 'amount']
        
class QueryParamGetTransactionSerializer(serializers.Serializer):
    dataRange = serializers.ChoiceField(choices=['today', 'weekly', 'monthly', 'all'], required=True)
    viewData = serializers.ChoiceField(choices=['group', 'all'], required=True)
    

class ResponseTransactionGroupSerializer(serializers.Serializer):
    category = serializers.CharField(source='category__name')
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)