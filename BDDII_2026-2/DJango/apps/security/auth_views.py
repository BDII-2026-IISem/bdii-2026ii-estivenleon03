from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken as JWTRefreshToken

from apps.security.serializers import (
    ErrorDetailSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    LogoutSerializer,
    RefreshResponseSerializer,
)
from apps.security.tokens import (
    RefreshTokenError,
    create_refresh_token,
    revoke_refresh,
    rotate_refresh,
)

User = get_user_model()


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
        },
    )
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

        refresh, _record = create_refresh_token(
            user,
            device_info=request.META.get("HTTP_USER_AGENT", ""),
        )
        access = str(AccessToken.for_user(user))
        access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        return Response(
            {
                "access": access,
                "refresh": refresh,
                "token_type": "Bearer",
                "tokenType": "Bearer",
                "access_expires_in": int(access_lifetime.total_seconds()),
                "accessExpiresIn": int(access_lifetime.total_seconds()),
            }
        )


class RefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: RefreshResponseSerializer,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
        },
    )
    def post(self, request):
        request_serializer = LogoutSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        raw_refresh = request_serializer.validated_data["refresh"]
        try:
            refresh, record = rotate_refresh(raw_refresh)
        except RefreshTokenError as exc:
            if raw_refresh.count(".") != 2 or str(exc) != "Refresh token desconocido.":
                return Response(
                    {"detail": str(exc)},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            serializer = TokenRefreshSerializer(data={"refresh": raw_refresh})
            try:
                serializer.is_valid(raise_exception=True)
            except (TokenError, ValidationError):
                return Response(
                    {"detail": "El refresh token no es válido o fue revocado."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(serializer.validated_data)
        access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        return Response(
            {
                "access": str(AccessToken.for_user(record.user)),
                "refresh": refresh,
                "accessExpiresIn": int(access_lifetime.total_seconds()),
            }
        )


class LogoutAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            204: None,
            400: ErrorDetailSerializer,
            401: ErrorDetailSerializer,
        },
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_refresh = serializer.validated_data["refresh"]
        if revoke_refresh(raw_refresh):
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            JWTRefreshToken(raw_refresh).blacklist()
        except TokenError:
            return Response(
                {"detail": "El refresh token no es válido o expiró."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
