from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.status import RecordStatus
from apps.security.models import Permission, Role, RolePermission, UserRole
from apps.security.serializers import (
    PermissionSerializer,
    ProfileSerializer,
    RolePermissionSerializer,
    RoleSerializer,
    UserRoleSerializer,
    UserSerializer,
)

User = get_user_model()


class ProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    lookup_value_converter = "int"

    def get_queryset(self):
        queryset = super().get_queryset()
        status_value = self.request.query_params.get("status")
        if status_value in (RecordStatus.ACTIVE, RecordStatus.INACTIVE):
            queryset = queryset.filter(is_active=status_value == RecordStatus.ACTIVE)
        return queryset

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class UserViewSet(SoftDeleteModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer

    @action(detail=True, methods=["get"], url_path="permissions")
    def permissions(self, request, pk=None):
        user = self.get_object()
        if user.pk != request.user.pk and not request.user.is_staff:
            return Response(
                {"detail": "No tiene autorización para consultar este perfil."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"permissions": _effective_permissions(user)})


class RoleViewSet(SoftDeleteModelViewSet):
    queryset = Role.objects.all().order_by("id")
    serializer_class = RoleSerializer


class PermissionViewSet(SoftDeleteModelViewSet):
    queryset = Permission.objects.all().order_by("id")
    serializer_class = PermissionSerializer


class UserRoleViewSet(SoftDeleteModelViewSet):
    queryset = UserRole.objects.select_related("role", "auth_user")
    serializer_class = UserRoleSerializer


class RolePermissionViewSet(SoftDeleteModelViewSet):
    queryset = RolePermission.objects.select_related("role", "permission")
    serializer_class = RolePermissionSerializer


def _effective_permissions(user):
    assignments = RolePermission.objects.filter(
        is_active=True,
        role__is_active=True,
        permission__is_active=True,
        role__user_assignments__auth_user=user,
        role__user_assignments__is_active=True,
    ).select_related("role", "permission")
    return [
        {
            "method": assignment.permission.http_method,
            "path": assignment.permission.resource,
            "roleId": assignment.role_id,
            "roleName": assignment.role.name,
        }
        for assignment in assignments
    ]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_permissions_view(request):
    return Response({"permissions": _effective_permissions(request.user)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
