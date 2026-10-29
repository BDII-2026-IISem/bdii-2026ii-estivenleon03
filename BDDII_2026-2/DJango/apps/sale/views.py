from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.product.models import Product
from .models import Sale, SalePayment
from .serializers import (
    SaleCreateSerializer,
    SalePaymentCreateSerializer,
    SaleSerializer,
    money,
)


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('owner', 'pet').prefetch_related(
        'items',
        'payments',
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return SaleCreateSerializer
        return SaleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()
        return Response(
            SaleSerializer(sale, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='payments')
    def add_payment(self, request, pk=None):
        payment_serializer = SalePaymentCreateSerializer(data=request.data)
        payment_serializer.is_valid(raise_exception=True)
        payment_data = payment_serializer.validated_data

        with transaction.atomic():
            sale = get_object_or_404(
                Sale.objects.select_for_update(),
                pk=pk,
            )
            self.check_object_permissions(request, sale)
            if not sale.is_active:
                raise ValidationError({'sale': 'No se puede pagar una venta anulada.'})

            paid_amount = sale.payments.filter(
                status=SalePayment.StatusChoices.PAID,
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            balance_due = money(sale.total - paid_amount)
            if payment_data['amount'] > balance_due:
                raise ValidationError({
                    'amount': f'El pago no puede superar el saldo pendiente ({balance_due:.2f}).',
                })

            SalePayment.objects.create(sale=sale, **payment_data)
            sale = self.get_queryset().get(pk=sale.pk)

        return Response(
            SaleSerializer(sale, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        self.get_object()
        sale = Sale.objects.select_for_update().get(pk=kwargs['pk'])
        if sale.is_active:
            items = list(sale.items.all().order_by('product_id'))
            product_ids = [item.product_id for item in items]
            products = list(
                Product.objects.select_for_update()
                .filter(pk__in=product_ids)
                .order_by('pk')
            )
            products_by_id = {product.pk: product for product in products}
            for item in items:
                product = products_by_id[item.product_id]
                product.stock += item.quantity
                product.save(update_fields=['stock', 'updated_at'])

            sale.is_active = False
            sale.save(update_fields=['is_active', 'updated_at'])
            sale.payments.exclude(
                status=SalePayment.StatusChoices.CANCELLED,
            ).update(status=SalePayment.StatusChoices.CANCELLED)

        return Response(status=status.HTTP_204_NO_CONTENT)
