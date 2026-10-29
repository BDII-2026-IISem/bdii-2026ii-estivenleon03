from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

from .models import Role, Permission, UserRole, RolePermission
from .models import User as RBACUser
from .serializers import (
    UserSerializer,
    RoleSerializer,
    PermissionSerializer,
    UserRoleSerializer,
    RolePermissionSerializer,
)

User = get_user_model()

# --- LOGIN INTACTO ---
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['password'].required = False

    def validate(self, attrs):
        data = self.initial_data
        identifier = data.get("username") or data.get("email") or data.get("identifier")
        password = data.get("password")

        if not identifier or not password:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Debe proporcionar usuario/correo y contraseña."})

        if "@" in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                identifier = user_obj.username
            except User.DoesNotExist:
                pass

        attrs["username"] = identifier
        attrs["password"] = password

        return super().validate(attrs)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

login_view = CustomTokenObtainPairView.as_view()

# --- VIEWSETS DE SEGURIDAD ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer

class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer


# --- ENDPOINT DE PERMISOS FORMATO EffectivePermission ---
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def user_permissions_view(request):
    rbac_user = RBACUser.objects.filter(
        email__iexact=request.user.email,
        is_active=True,
    ).first()
    if rbac_user is None:
        return Response({'permissions': []}, status=status.HTTP_200_OK)

    role_ids = UserRole.objects.filter(user=rbac_user).values_list('role_id', flat=True)
    role_permissions = RolePermission.objects.filter(
        role_id__in=role_ids,
    ).select_related('role', 'permission')
    effective_permissions = [
        {
            'method': assignment.permission.http_method,
            'path': assignment.permission.resource,
            'roleId': assignment.role_id,
            'roleName': assignment.role.name,
        }
        for assignment in role_permissions
    ]

    return Response({
        'permissions': effective_permissions
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def user_profile_view(request):
    serializer = UserSerializer(request.user)
    data = serializer.data
    data['status'] = 'ACTIVE'
    data['avatar'] = None
    return Response(data, status=status.HTTP_200_OK)
