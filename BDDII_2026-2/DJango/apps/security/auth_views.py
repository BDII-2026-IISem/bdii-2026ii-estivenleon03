import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from drf_spectacular.utils import extend_schema

from apps.common.status import RecordStatus
from apps.security.models import RefreshToken
from apps.security.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
    TokenPairSerializer,
)
from apps.security.tokens import generate_refresh_value, hash_token

User = get_user_model()

def token_payload(user, raw_refresh):
    access = AccessToken.for_user(user)
    lifetime = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
    return {
        "access": str(access),
        "refresh": raw_refresh,
        "token_type": "Bearer",
        "access_expires_in": lifetime,
    }

def issue_refresh(user, family_id=None):
    raw_refresh = generate_refresh_value()
    stored = RefreshToken.objects.create(
        user=user,
        token_hash=hash_token(raw_refresh),
        family_id=family_id or uuid.uuid4(),
        expires_at=RefreshToken.default_expiry(),
        status=RecordStatus.ACTIVE,
    )
    return stored, raw_refresh

class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: TokenPairSerializer},
        operation_id="auth_login",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = _find_user(data.get("username"), data.get("email"))
        invalid = Response(
            {"detail": "Credenciales inválidas."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
        if user is None or user.status != RecordStatus.ACTIVE:
            return invalid
        if not user.check_password(data["password"]):
            return invalid
        _stored, raw_refresh = issue_refresh(user)
        return Response(token_payload(user, raw_refresh), status=status.HTTP_200_OK)

class RefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=RefreshSerializer,
        responses={200: TokenPairSerializer},
        operation_id="auth_refresh",
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_token = serializer.validated_data["refresh"]
        token_hash_val = hash_token(raw_token)

        invalid_response = Response(
            {"detail": "Token no válido o expirado."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

        with transaction.atomic():
            token = (
                RefreshToken.objects.select_for_update()
                .select_related("user")
                .filter(token_hash=token_hash_val)
                .first()
            )

            if not token:
                return invalid_response

            if (
                token.replaced_by_id is not None
                or token.revoked_at is not None
                or token.status != RecordStatus.ACTIVE
            ):
                RefreshToken.objects.filter(family_id=token.family_id).update(
                    status=RecordStatus.INACTIVE,
                    revoked_at=timezone.now(),
                )
                return invalid_response

            if token.expires_at <= timezone.now() or token.user.status != RecordStatus.ACTIVE:
                token.status = RecordStatus.INACTIVE
                token.save(update_fields=["status", "updated_at"])
                return invalid_response

            new_stored, new_raw_refresh = issue_refresh(
                user=token.user,
                family_id=token.family_id,
            )
            token.replaced_by = new_stored
            token.status = RecordStatus.INACTIVE
            token.save(update_fields=["replaced_by", "status", "updated_at"])

            return Response(
                token_payload(token.user, new_raw_refresh),
                status=status.HTTP_200_OK,
            )

class LogoutAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=LogoutSerializer,
        responses={204: None},
        operation_id="auth_logout",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_token = serializer.validated_data["refresh"]
        token_hash_val = hash_token(raw_token)

        invalid_response = Response(
            {"detail": "Token no válido o expirado."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

        with transaction.atomic():
            token = (
                RefreshToken.objects.select_for_update()
                .filter(token_hash=token_hash_val)
                .first()
            )

            if not token:
                return invalid_response

            if token.replaced_by_id is not None:
                RefreshToken.objects.filter(family_id=token.family_id).update(
                    status=RecordStatus.INACTIVE,
                    revoked_at=timezone.now(),
                )
                return invalid_response

            token.status = RecordStatus.INACTIVE
            if not token.revoked_at:
                token.revoked_at = timezone.now()
            token.save(update_fields=["status", "revoked_at", "updated_at"])

            return Response(status=status.HTTP_204_NO_CONTENT)

def _find_user(username, email):
    if username and email:
        return User.objects.filter(username=username, email__iexact=email).first()
    if username:
        return User.objects.filter(username=username).first()
    if email:
        return User.objects.filter(email__iexact=email).first()
    return None
