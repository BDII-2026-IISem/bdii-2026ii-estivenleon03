from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Veterinarian
from apps.security.models import User


class VeterinarianUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email')


class VeterinarianAuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email')


class VeterinarianSerializer(serializers.ModelSerializer):
    auth_user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False,
        allow_null=True,
    )
    user_details = VeterinarianUserSerializer(source='user', read_only=True)
    auth_user_details = VeterinarianAuthUserSerializer(
        source='auth_user',
        read_only=True,
    )

    class Meta:
        model = Veterinarian
        fields = (
            'id',
            'name',
            'license_number',
            'description',
            'is_active',
            'auth_user',
            'user_details',
            'auth_user_details',
        )
        read_only_fields = ('id', 'user_details', 'auth_user_details')

    def validate_auth_user(self, auth_user):
        if auth_user is None:
            return auth_user
        if (
            not auth_user.is_active
            and (
                self.instance is None
                or self.instance.auth_user_id != auth_user.pk
            )
        ):
            raise serializers.ValidationError(
                'Solo se pueden asignar cuentas activas.'
            )
        assignments = Veterinarian.objects.filter(auth_user=auth_user)
        if self.instance is not None:
            assignments = assignments.exclude(pk=self.instance.pk)
        if assignments.exists():
            raise serializers.ValidationError(
                'Esta cuenta ya está vinculada a otro perfil veterinario.'
            )
        return auth_user
