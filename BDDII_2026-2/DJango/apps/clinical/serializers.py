from rest_framework import serializers
from .models import Consultation, Prescription, Vaccine, VaccineBatch, VaccineApplication

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = '__all__'

class VaccineBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineBatch
        fields = '__all__'

class VaccineApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineApplication
        fields = '__all__'
