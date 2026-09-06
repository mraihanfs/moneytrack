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
        queryset=Category.objects.all(),
        slug_field='name'
    )
    
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'category', 'user']
        
        
class ResponseTransactionSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'category', 'user', 'created_at', 'amount']