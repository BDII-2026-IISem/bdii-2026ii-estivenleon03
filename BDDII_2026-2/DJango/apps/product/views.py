from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product, ProductType
from .serializers import ProductSerializer, ProductTypeSerializer


class StatusFilteredViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter is None:
            return queryset
        if status_filter not in ('active', 'inactive'):
            raise serializers.ValidationError(
                {'status': 'El estado debe ser active o inactive.'}
            )
        return queryset.filter(is_active=(status_filter == 'active'))

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])


class ProductTypeViewSet(StatusFilteredViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer

    def perform_destroy(self, instance):
        if instance.products.filter(is_active=True).exists():
            raise serializers.ValidationError(
                'Desactiva primero los productos asociados a este tipo.'
            )
        super().perform_destroy(instance)


class ProductViewSet(StatusFilteredViewSet):
    queryset = Product.objects.select_related('product_type').all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def available(self, request):
        products = self.get_queryset().filter(
            is_active=True,
            stock__gt=0,
            product_type__is_active=True,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
