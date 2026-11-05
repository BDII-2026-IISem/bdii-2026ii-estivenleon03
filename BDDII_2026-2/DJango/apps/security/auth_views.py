from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.security.serializers import LoginSerializer, LogoutSerializer

User = get_user_model()


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credentials = serializer.validated_data
        identifier = credentials.get("username") or credentials.get("email")
        username = identifier

        email = credentials.get("email")
        if email or "@" in identifier:
            email = email or identifier
            matches = list(
                User.objects.filter(email__iexact=email, is_active=True)[:2]
            )
            if len(matches) != 1:
                return Response(
                    {"detail": "Credenciales inválidas."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user_by_email = matches[0]
            if credentials.get("username") and credentials["username"] != user_by_email.get_username():
                return Response(
                    {"detail": "Credenciales inválidas."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            username = user_by_email.get_username()

        user = authenticate(
            request,
            username=username,
            password=credentials["password"],
        )
        if user is None:
            return Response(
                {"detail": "Credenciales inválidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "token_type": "Bearer",
                "access_expires_in": int(access_lifetime.total_seconds()),
            }
        )


class RefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"detail": "El refresh token no es válido o fue revocado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(serializer.validated_data)


class LogoutAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return Response(
                {"detail": "El refresh token no es válido o expiró."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
