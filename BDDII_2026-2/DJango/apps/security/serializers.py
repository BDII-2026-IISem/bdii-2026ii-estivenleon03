from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, Permission, UserRole, RolePermission

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='username', read_only=True)
    password_hash = serializers.CharField(source='password', write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'password_hash', 'is_active']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'
