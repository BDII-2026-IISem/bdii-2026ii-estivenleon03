from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import BaseModel


class ProductType(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'product_types'
        ordering = ['name', 'id']
        verbose_name = 'tipo de producto'
        verbose_name_plural = 'tipos de producto'

    def __str__(self):
        return self.name


class Product(BaseModel):
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.RESTRICT,
        related_name='products',
        db_column='product_type_id',
    )
    name = models.CharField(max_length=120, unique=True)
    brand = models.CharField(max_length=80)
    description = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )
    min_stock = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'products'
        ordering = ['name', 'id']
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='product_price_non_neg',
            ),
        ]

    def __str__(self):
        return self.name
