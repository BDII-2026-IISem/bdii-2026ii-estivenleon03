from decimal import Decimal

from rest_framework import serializers
from .models import Payment, PaymentAudit

class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )

    class Meta:
        model = Payment
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        appointment = attrs.get(
            'appointment',
            self.instance.appointment if self.instance else None,
        )
        reference_type = attrs.get(
            'reference_type',
            self.instance.reference_type if self.instance else 'APPOINTMENT',
        )
        reference_id = attrs.get(
            'reference_id',
            self.instance.reference_id if self.instance else None,
        )

        if reference_type != 'APPOINTMENT':
            raise serializers.ValidationError({
                'reference_type': 'Los pagos de esta tabla deben corresponder a una cita.'
            })
        if appointment is not None and reference_id != appointment.pk:
            raise serializers.ValidationError({
                'reference_id': 'La referencia debe coincidir con la cita seleccionada.'
            })
        return attrs

class PaymentAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAudit
        fields = '__all__'
        read_only_fields = (
            'id',
            'payment_id',
            'actionSale',
            'changed_at',
            'changed_by',
            'before_data',
            'after_data',
        )
