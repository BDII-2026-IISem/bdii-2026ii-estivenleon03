from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class StoreLabJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not getattr(user, 'is_active', True):
            raise AuthenticationFailed('El usuario no está active.', code='user_inactive')
        return user
