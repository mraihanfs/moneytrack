from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from django.contrib.auth import get_user_model

User = get_user_model()

class HasApiKeyWithName(HasAPIKey):
    def has_permission(self, request, view):
        is_valid = super().has_permission(request, view)
        if is_valid:
            api_key = self.get_key(request)
            if api_key:
                try:
                    api_key_instance = APIKey.objects.get_from_key(api_key)
                    if api_key_instance:
                        request.api_key_name = api_key_instance.name
                        return True
                except APIKey.DoesNotExist:
                    return False
            return False
        return False