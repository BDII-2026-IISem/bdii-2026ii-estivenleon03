from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Product, ProductType


class StatusField(serializers.Field):
    def to_representation(self, value):
        return 'active' if value else 'inactive'

    def to_internal_value(self, data):
        if data not in ('active', 'inactive'):
            raise serializers.ValidationError('El estado debe ser active o inactive.')
        return data == 'active'


class ProductTypeSerializer(serializers.ModelSerializer):
    status = StatusField(source='is_active', required=False)
    name = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=ProductType.objects.all())],
    )

    class Meta:
        model = ProductType
        fields = ('id', 'name', 'description', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return value


class ProductSerializer(serializers.ModelSerializer):
    productTypeId = serializers.PrimaryKeyRelatedField(
        source='product_type',
        queryset=ProductType.objects.filter(is_active=True),
    )
    productTypeName = serializers.CharField(source='product_type.name', read_only=True)
    minStock = serializers.IntegerField(source='min_stock', min_value=0, required=False)
    quantity = serializers.IntegerField(source='stock', min_value=0, required=False)
    status = StatusField(source='is_active', required=False)
    name = serializers.CharField(
        max_length=120,
        validators=[UniqueValidator(queryset=Product.objects.all())],
    )
    brand = serializers.CharField(max_length=80)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)

    class Meta:
        model = Product
        fields = (
            'id',
            'productTypeId',
            'productTypeName',
            'name',
            'brand',
            'description',
            'price',
            'minStock',
            'quantity',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'productTypeName', 'created_at', 'updated_at')

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('El nombre debe tener al menos 2 caracteres.')
        return value

    def validate_brand(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('La marca o laboratorio es obligatorio.')
        return value

    def validate(self, attrs):
        product_type = attrs.get(
            'product_type',
            self.instance.product_type if self.instance is not None else None,
        )
        if product_type is not None and not product_type.is_active:
            raise serializers.ValidationError(
                {'productTypeId': 'El tipo seleccionado está inactivo.'}
            )
        is_active = attrs.get(
            'is_active',
            self.instance.is_active if self.instance is not None else True,
        )
        if is_active and not product_type.is_active:
            raise serializers.ValidationError(
                {'status': 'No se puede activar un producto asociado a un tipo inactivo.'}
            )
        return attrs
