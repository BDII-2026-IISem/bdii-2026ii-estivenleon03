from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from rest_framework import serializers

from apps.patient.models import Owner, Pet
from apps.product.models import Product
from .models import Sale, SaleItem, SalePayment


CENT = Decimal('0.01')
TAX_RATE = Decimal('0.19')


def money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class SaleItemInputSerializer(serializers.Serializer):
    productId = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class SaleCreateSerializer(serializers.Serializer):
    clientId = serializers.PrimaryKeyRelatedField(
        queryset=Owner.objects.all(),
        source='owner',
    )
    petId = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.all(),
        source='pet',
        required=False,
        allow_null=True,
    )
    saleDate = serializers.DateTimeField(source='sale_date')
    discounts = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.00'),
        required=False,
        default=Decimal('0.00'),
    )
    items = SaleItemInputSerializer(many=True, allow_empty=False)
    paymentMethod = serializers.ChoiceField(
        choices=SalePayment.MethodChoices.choices,
        required=False,
        allow_null=True,
    )
    paymentAmount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        pet = attrs.get('pet')
        owner = attrs['owner']
        if pet is not None and pet.owner_id != owner.pk:
            raise serializers.ValidationError({
                'petId': 'La mascota seleccionada no pertenece al propietario.',
            })

        product_ids = [item['productId'] for item in attrs['items']]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError({
                'items': 'No repitas productos; envía una sola línea por producto.',
            })

        has_method = attrs.get('paymentMethod') is not None
        has_amount = attrs.get('paymentAmount') is not None
        if has_method != has_amount:
            raise serializers.ValidationError({
                'payment': 'paymentMethod y paymentAmount deben enviarse juntos.',
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        lines = validated_data.pop('items')
        payment_method = validated_data.pop('paymentMethod', None)
        payment_amount = validated_data.pop('paymentAmount', None)
        product_ids = [line['productId'] for line in lines]

        products = list(
            Product.objects.select_for_update()
            .select_related('product_type')
            .filter(pk__in=product_ids)
            .order_by('pk')
        )
        products_by_id = {product.pk: product for product in products}
        missing_ids = sorted(set(product_ids) - set(products_by_id))
        if missing_ids:
            raise serializers.ValidationError({
                'items': f'Producto(s) no encontrado(s): {", ".join(map(str, missing_ids))}.',
            })

        subtotal = Decimal('0.00')
        for line in lines:
            product = products_by_id[line['productId']]
            if not product.is_active or not product.product_type.is_active:
                raise serializers.ValidationError({
                    'items': f'El producto "{product.name}" está inactivo.',
                })
            if product.stock < line['quantity']:
                raise serializers.ValidationError({
                    'items': f'Stock insuficiente para "{product.name}". Disponible: {product.stock}.',
                })
            subtotal += product.price * line['quantity']
        subtotal = money(subtotal)

        discounts = validated_data.pop('discounts', Decimal('0.00'))
        if discounts > subtotal:
            raise serializers.ValidationError({
                'discounts': 'El descuento no puede superar el subtotal.',
            })
        tax = money((subtotal - discounts) * TAX_RATE)
        total = money(subtotal - discounts + tax)
        if payment_amount is not None and payment_amount > total:
            raise serializers.ValidationError({
                'paymentAmount': 'El pago inicial no puede superar el total de la venta.',
            })

        sale = Sale.objects.create(
            **validated_data,
            subtotal=subtotal,
            tax=tax,
            discounts=discounts,
            total=total,
        )
        for line in lines:
            product = products_by_id[line['productId']]
            quantity = line['quantity']
            SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price,
                line_total=money(product.price * quantity),
            )
            product.stock -= quantity
            product.save(update_fields=['stock', 'updated_at'])

        if payment_amount is not None:
            SalePayment.objects.create(
                sale=sale,
                method=payment_method,
                amount=payment_amount,
            )
        return sale


class SaleItemSerializer(serializers.ModelSerializer):
    productId = serializers.IntegerField(source='product_id', read_only=True)
    productName = serializers.CharField(source='product_name', read_only=True)
    unitPrice = serializers.DecimalField(
        source='unit_price',
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    lineTotal = serializers.DecimalField(
        source='line_total',
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = SaleItem
        fields = ['productId', 'productName', 'quantity', 'unitPrice', 'lineTotal']


class SalePaymentSerializer(serializers.ModelSerializer):
    paymentDate = serializers.DateTimeField(source='payment_date', read_only=True)

    class Meta:
        model = SalePayment
        fields = ['id', 'method', 'amount', 'paymentDate', 'status']
        read_only_fields = fields


class SalePaymentCreateSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=SalePayment.MethodChoices.choices)
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )


class SaleSerializer(serializers.ModelSerializer):
    client = serializers.IntegerField(source='owner_id', read_only=True)
    clientName = serializers.CharField(source='owner.name', read_only=True)
    pet = serializers.IntegerField(source='pet_id', read_only=True, allow_null=True)
    petName = serializers.CharField(source='pet.name', read_only=True, allow_null=True)
    saleDate = serializers.DateTimeField(source='sale_date', read_only=True)
    status = serializers.SerializerMethodField()
    paymentStatus = serializers.SerializerMethodField()
    paidAmount = serializers.SerializerMethodField()
    balanceDue = serializers.SerializerMethodField()
    items = SaleItemSerializer(many=True, read_only=True)
    payments = SalePaymentSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discounts = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id',
            'client',
            'clientName',
            'pet',
            'petName',
            'saleDate',
            'subtotal',
            'tax',
            'discounts',
            'total',
            'status',
            'paymentStatus',
            'paidAmount',
            'balanceDue',
            'items',
            'payments',
        ]

    def get_status(self, sale):
        return 'active' if sale.is_active else 'inactive'

    def get_paidAmount(self, sale):
        if not sale.is_active:
            return '0.00'
        paid = sum(
            (payment.amount for payment in sale.payments.all()
             if payment.status == SalePayment.StatusChoices.PAID),
            Decimal('0.00'),
        )
        return format(money(paid), '.2f')

    def get_balanceDue(self, sale):
        if not sale.is_active:
            return '0.00'
        paid = sum(
            (payment.amount for payment in sale.payments.all()
             if payment.status == SalePayment.StatusChoices.PAID),
            Decimal('0.00'),
        )
        return format(money(max(sale.total - paid, Decimal('0.00'))), '.2f')

    def get_paymentStatus(self, sale):
        if not sale.is_active:
            return 'CANCELLED'
        paid = sum(
            (payment.amount for payment in sale.payments.all()
             if payment.status == SalePayment.StatusChoices.PAID),
            Decimal('0.00'),
        )
        if paid >= sale.total:
            return 'PAID'
        return 'PARTIAL' if paid > 0 else 'PENDING'
