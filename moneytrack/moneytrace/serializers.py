from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        groups = self.user.groups.all().values_list('name', flat=True)
        data["groups"] =list(groups)
        
        return data