from rest_framework import serializers
from .models import Veterinarian
from apps.security.models import User


class VeterinarianUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email')

class VeterinarianSerializer(serializers.ModelSerializer):
    user_details = VeterinarianUserSerializer(source='user', read_only=True)

    class Meta:
        model = Veterinarian
        fields = '__all__'
