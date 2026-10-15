from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models, transaction
from apps.common.status import RecordStatus
from apps.product.models import Product

class SaleQuerySet(models.QuerySet):
    def register(self, *, client, sale_date, items, discounts):
        if not items:
            raise ValidationError({"items": ["La venta requiere al menos un producto."]})
        discounts = Decimal(discounts).quantize(Decimal("0.01"))
        if discounts < 0:
            raise ValidationError({"discounts": ["El descuento no puede ser negativo."]})
        quantities = {}
        for item in items:
            quantity = int(item["quantity"])
            if quantity < 1:
                raise ValidationError({"items": ["La cantidad debe ser al menos 1."]})
            product_id = item["product_id"]
            quantities[product_id] = quantities.get(product_id, 0) + quantity
        with transaction.atomic():
            locked_client = client.__class__.objects.select_for_update().get(pk=client.pk)
            if locked_client.status != RecordStatus.ACTIVE:
                raise ValidationError({"client_id": ["El cliente debe estar active."]})
            locked_products = {
                product.id: product
                for product in Product.objects.select_for_update()
                .select_related("product_type")
                .filter(pk__in=quantities)
                .order_by("id")
            }
            if len(locked_products) != len(quantities):
                raise ValidationError({"items": ["Hay productos que no existen."]})
            for product_id, quantity in quantities.items():
                product = locked_products[product_id]
                if product.status != RecordStatus.ACTIVE:
                    raise ValidationError(
                        {"items": [f"El producto {product.name} no está active."]}
                    )
                if product.product_type.status != RecordStatus.ACTIVE:
                    raise ValidationError(
                        {"items": [f"El tipo de {product.name} no está active."]}
                    )
                if product.stock < quantity:
                    raise ValidationError(
                        {"items": [f"Stock insuficiente para {product.name}."]}
                    )
            sale = self.model(
                client=locked_client,
                sale_date=sale_date,
                subtotal=Decimal("0.00"),
                tax=Decimal("0.00"),
                discounts=discounts,
                total=Decimal("0.00"),
                status=RecordStatus.INACTIVE,
            )
            sale.save()
            subtotal = Decimal("0.00")
            for item in items:
                product = locked_products[item["product_id"]]
                unit_price = product.price
                quantity = int(item["quantity"])
                line_total = (unit_price * quantity).quantize(Decimal("0.01"))
                sale.lines.create(
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                    status=RecordStatus.ACTIVE,
                )
                subtotal += line_total
            subtotal = subtotal.quantize(Decimal("0.01"))
            if discounts > subtotal:
                raise ValidationError(
                    {"discounts": ["El descuento no puede superar el subtotal."]}
                )
            tax = Decimal("0.00")
            total = (subtotal + tax - discounts).quantize(Decimal("0.01"))
            sale.subtotal = subtotal
            sale.tax = tax
            sale.discounts = discounts
            sale.total = total
            sale.status = RecordStatus.ACTIVE
            sale.save(
                update_fields=[
                    "subtotal",
                    "tax",
                    "discounts",
                    "total",
                    "status",
                    "updated_at",
                ]
            )
            for product_id, quantity in quantities.items():
                product = locked_products[product_id]
                product.stock -= quantity
                product.save(update_fields=["stock", "updated_at"])
            return sale

class SaleManager(models.Manager.from_queryset(SaleQuerySet)):
    pass
