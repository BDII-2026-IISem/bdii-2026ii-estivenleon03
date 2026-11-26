from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from .models import Permission, Role, RolePermission, UserProfile, UserRole

User = get_user_model()
ASSIGNABLE_ROLE_NAMES = ("ADMIN", "VETERINARIO", "RECEPCIONISTA", "PROPIETARIO")


@extend_schema_field(OpenApiTypes.STR)
class StatusField(serializers.Field):
    def to_representation(self, value):
        return "active" if value else "inactive"

    def to_internal_value(self, data):
        if data == "active":
            return True
        if data == "inactive":
            return False
        raise serializers.ValidationError("El estado debe ser active o inactive.")


@extend_schema_field(OpenApiTypes.STR)
class AvatarField(serializers.Field):
    def get_attribute(self, user):
        return user

    def to_representation(self, user):
        profile = UserProfile.objects.filter(user=user).only("avatar").first()
        return profile.avatar if profile else None

    def to_internal_value(self, data):
        return serializers.URLField(allow_null=True, allow_blank=True).run_validation(data)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    avatar = AvatarField(required=False)
    status = StatusField(source="is_active", required=False)
    isStaff = serializers.BooleanField(source="is_staff", read_only=True)
    isSuperuser = serializers.BooleanField(source="is_superuser", read_only=True)
    firstName = serializers.CharField(source="first_name", required=False, allow_blank=True)
    lastName = serializers.CharField(source="last_name", required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "email",
            "avatar",
            "status",
            "isStaff",
            "isSuperuser",
            "firstName",
            "lastName",
            "password",
        )
        read_only_fields = ("id", "name", "isStaff", "isSuperuser")

    @extend_schema_field(OpenApiTypes.STR)
    def get_name(self, user):
        return user.get_full_name() or user.username

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        avatar = validated_data.pop("avatar", None)
        if not password:
            raise serializers.ValidationError({"password": "La contraseña es obligatoria."})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if avatar is not None:
            UserProfile.objects.create(user=user, avatar=avatar)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        avatar = validated_data.pop("avatar", serializers.empty)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        if avatar is not serializers.empty:
            UserProfile.objects.update_or_create(
                user=instance,
                defaults={"avatar": avatar},
            )
        return instance


class ProfileSerializer(UserSerializer):

    class Meta:
        model = UserSerializer.Meta.model
        fields = (
            "id",
            "username",
            "name",
            "email",
            "avatar",
            "status",
            "firstName",
            "lastName",
            "isStaff",
            "isSuperuser",
        )
        read_only_fields = (
            "id",
            "username",
            "name",
            "status",
            "isStaff",
            "isSuperuser",
        )


class RoleSerializer(serializers.ModelSerializer):
    status = StatusField(source="is_active", required=False)

    class Meta:
        model = Role
        fields = ("id", "name", "description", "status", "created_at")
        read_only_fields = ("id", "created_at")


class PermissionSerializer(serializers.ModelSerializer):
    method = serializers.CharField(source="http_method")
    path = serializers.CharField(source="resource")
    status = StatusField(source="is_active", required=False)

    class Meta:
        model = Permission
        fields = ("id", "method", "path", "description", "status")
        read_only_fields = ("id",)


class UserRoleSerializer(serializers.ModelSerializer):
    userId = serializers.PrimaryKeyRelatedField(
        source="auth_user",
        queryset=User.objects.all(),
    )
    roleId = serializers.PrimaryKeyRelatedField(
        source="role",
        queryset=Role.objects.filter(
            name__in=ASSIGNABLE_ROLE_NAMES,
            is_active=True,
        ),
    )
    status = StatusField(source="is_active", required=False)

    class Meta:
        model = UserRole
        fields = ("id", "userId", "roleId", "status")
        read_only_fields = ("id",)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        auth_user = attrs.get(
            "auth_user",
            self.instance.auth_user if self.instance else None,
        )
        is_active = attrs.get(
            "is_active",
            self.instance.is_active if self.instance else True,
        )
        if auth_user:
            is_same_user = (
                self.instance is not None
                and self.instance.auth_user_id == auth_user.pk
            )
            if not auth_user.is_active and (is_active or not is_same_user):
                raise serializers.ValidationError({
                    "userId": "No se puede asignar un rol a un usuario inactivo."
                })
        if auth_user and is_active:
            assignments = UserRole.objects.filter(auth_user=auth_user, is_active=True)
            if self.instance:
                assignments = assignments.exclude(pk=self.instance.pk)
            if assignments.exists():
                raise serializers.ValidationError({
                    "userId": "El usuario ya tiene una asignación activa. Edita el rol existente."
                })
        return attrs


class RolePermissionSerializer(serializers.ModelSerializer):
    roleId = serializers.PrimaryKeyRelatedField(source="role", queryset=Role.objects.all())
    resourceId = serializers.PrimaryKeyRelatedField(
        source="permission",
        queryset=Permission.objects.all(),
    )
    status = StatusField(source="is_active", required=False)

    class Meta:
        model = RolePermission
        fields = ("id", "roleId", "resourceId", "status")
        read_only_fields = ("id",)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if not (attrs.get("username") or attrs.get("email")):
            raise serializers.ValidationError("Debe proporcionar usuario o correo.")
        return attrs


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutSerializer(RefreshSerializer):
    pass


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    token_type = serializers.CharField()
    access_expires_in = serializers.IntegerField()


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    token_type = serializers.CharField()
    tokenType = serializers.CharField()
    access_expires_in = serializers.IntegerField()
    accessExpiresIn = serializers.IntegerField()


class RefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)
    accessExpiresIn = serializers.IntegerField(required=False)


class ErrorDetailSerializer(serializers.Serializer):
    detail = serializers.CharField()


class EffectivePermissionSerializer(serializers.Serializer):
    method = serializers.CharField()
    path = serializers.CharField()
    roleId = serializers.IntegerField()
    roleName = serializers.CharField()


class EffectivePermissionsSerializer(serializers.Serializer):
    permissions = EffectivePermissionSerializer(many=True)
