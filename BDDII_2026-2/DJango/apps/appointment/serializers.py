from rest_framework import serializers
from .models import Appointment
from apps.patient.serializers import PetSerializer
from apps.staff.serializers import VeterinarianSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    pet_details = PetSerializer(source='pet', read_only=True)
    veterinarian_details = VeterinarianSerializer(source='veterinarian', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
