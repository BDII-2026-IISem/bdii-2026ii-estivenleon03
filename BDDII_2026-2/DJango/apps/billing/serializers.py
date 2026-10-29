from rest_framework import serializers
from .models import Payment, PaymentAudit

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAudit
        fields = '__all__'
