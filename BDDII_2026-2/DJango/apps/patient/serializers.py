from rest_framework import serializers
from .models import Owner, Pet

class OwnerSerializer(serializers.ModelSerializer):
    doc_type = serializers.CharField(default='CC', required=False, allow_blank=True)
    doc_number = serializers.CharField(source='document_number', required=False, allow_blank=True)

    class Meta:
        model = Owner
        fields = '__all__'

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = '__all__'
