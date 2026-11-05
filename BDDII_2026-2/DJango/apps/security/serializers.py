from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Permission, Role, RolePermission, UserProfile, UserRole

User = get_user_model()


class StatusField(serializers.Field):
    def to_representation(self, value):
        return "active" if value else "inactive"

    def to_internal_value(self, data):
        if data == "active":
            return True
        if data == "inactive":
            return False
        raise serializers.ValidationError("El estado debe ser active o inactive.")


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
    roleId = serializers.PrimaryKeyRelatedField(source="role", queryset=Role.objects.all())
    status = StatusField(source="is_active", required=False)

    class Meta:
        model = UserRole
        fields = ("id", "userId", "roleId", "status")
        read_only_fields = ("id",)


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
