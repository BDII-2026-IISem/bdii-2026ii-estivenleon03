from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Owner, Pet


class OwnerStatusField(serializers.Field):
    def to_representation(self, value):
        return 'active' if value else 'inactive'

    def to_internal_value(self, data):
        if data not in ('active', 'inactive'):
            raise serializers.ValidationError('El estado debe ser active o inactive.')
        return data == 'active'


class OwnerSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='name', max_length=120)
    documento = serializers.CharField(
        source='doc_number',
        max_length=30,
        validators=[UniqueValidator(queryset=Owner.objects.all())],
    )
    doc_type = serializers.CharField(default='CC', required=False, allow_blank=True)
    telefono = serializers.CharField(source='phone', required=False, allow_blank=True, allow_null=True)
    direccion = serializers.CharField(source='address', required=False, allow_blank=True, allow_null=True)
    status = OwnerStatusField(source='is_active', required=False)

    class Meta:
        model = Owner
        fields = (
            'id',
            'nombre',
            'documento',
            'doc_type',
            'telefono',
            'email',
            'direccion',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = '__all__'
