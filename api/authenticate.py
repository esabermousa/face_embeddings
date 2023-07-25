# Third Parties
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_api_key.models import APIKey


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get("HTTP_AUTHORIZATION")

        if not api_key:
            return None

        try:
            APIKey.objects.get_from_key(api_key.split()[1])
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key.")

        return (None, None)
