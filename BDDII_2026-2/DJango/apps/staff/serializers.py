from rest_framework import serializers
from .models import Veterinarian
from apps.security.serializers import UserSerializer

class VeterinarianSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Veterinarian
        fields = '__all__'
