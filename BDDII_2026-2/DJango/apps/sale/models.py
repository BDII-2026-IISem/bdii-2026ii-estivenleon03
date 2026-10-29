from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import BaseModel


class Sale(BaseModel):
    owner = models.ForeignKey(
        'patient.Owner',
        on_delete=models.RESTRICT,
        related_name='sales',
        db_column='owner_id',
        db_constraint=False,
    )
    pet = models.ForeignKey(
        'patient.Pet',
        on_delete=models.SET_NULL,
        related_name='sales',
        db_column='pet_id',
        null=True,
        blank=True,
        db_constraint=False,
    )
    sale_date = models.DateTimeField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discounts = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'sales'
        ordering = ['-sale_date', '-id']
        constraints = [
            models.CheckConstraint(condition=models.Q(subtotal__gte=0), name='sale_subtotal_non_neg'),
            models.CheckConstraint(condition=models.Q(tax__gte=0), name='sale_tax_non_neg'),
            models.CheckConstraint(condition=models.Q(discounts__gte=0), name='sale_discount_non_neg'),
            models.CheckConstraint(condition=models.Q(total__gte=0), name='sale_total_non_neg'),
        ]

    def __str__(self):
        return f'Sale #{self.pk}'


class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='sale_id',
    )
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.RESTRICT,
        related_name='sale_items',
        db_column='product_id',
    )
    product_name = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'sale_items'
        ordering = ['id']
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gt=0), name='sale_item_quantity_positive'),
            models.CheckConstraint(condition=models.Q(unit_price__gte=0), name='sale_item_price_non_neg'),
            models.CheckConstraint(condition=models.Q(line_total__gte=0), name='sale_item_total_non_neg'),
        ]

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'


class SalePayment(models.Model):
    class MethodChoices(models.TextChoices):
        CASH = 'CASH', 'Cash'
        DEBIT_CARD = 'DEBIT_CARD', 'Debit Card'
        CREDIT_CARD = 'CREDIT_CARD', 'Credit Card'
        TRANSFER = 'TRANSFER', 'Transfer'

    class StatusChoices(models.TextChoices):
        PAID = 'PAID', 'Paid'
        CANCELLED = 'CANCELLED', 'Cancelled'

    sale = models.ForeignKey(
        Sale,
        on_delete=models.RESTRICT,
        related_name='payments',
        db_column='sale_id',
    )
    method = models.CharField(max_length=20, choices=MethodChoices.choices)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PAID,
    )

    class Meta:
        db_table = 'sale_payments'
        ordering = ['id']
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name='sale_payment_amount_positive'),
        ]

    def __str__(self):
        return f'{self.method} payment for sale #{self.sale_id}'
