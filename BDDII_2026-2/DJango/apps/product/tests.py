from rest_framework import status
from rest_framework.test import APITestCase
from decimal import Decimal

from apps.product.models import Product, ProductType


class ProductInventoryApiTests(APITestCase):
    products_endpoint = '/api/v1/products/'
    types_endpoint = '/api/v1/product-types/'

    def setUp(self):
        self.product_type = ProductType.objects.create(name='Medicamentos')

    def product_payload(self, **overrides):
        return {
            'productTypeId': self.product_type.pk,
            'name': 'Amoxicilina 250 mg',
            'brand': 'Laboratorio Vet',
            'description': 'Suspensión oral',
            'price': '18500.00',
            'minStock': 5,
            'quantity': 20,
            'status': 'active',
            **overrides,
        }

    def test_product_crud_uses_veterinary_inventory_fields(self):
        created = self.client.post(
            self.products_endpoint,
            self.product_payload(),
            format='json',
        )

        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data['productTypeName'], 'Medicamentos')
        self.assertEqual(created.data['quantity'], 20)
        self.assertEqual(created.data['minStock'], 5)
        product = Product.objects.get(pk=created.data['id'])
        self.assertEqual(product.stock, 20)
        self.assertEqual(product.price, Decimal('18500.00'))

        updated = self.client.patch(
            f'{self.products_endpoint}{product.pk}/',
            {'quantity': 3},
            format='json',
        )

        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.stock, 3)

    def test_available_products_excludes_zero_stock_and_inactive_category(self):
        available = Product.objects.create(
            product_type=self.product_type,
            name='Producto disponible',
            brand='Vet',
            price='2000.00',
            stock=1,
        )
        Product.objects.create(
            product_type=self.product_type,
            name='Producto agotado',
            brand='Vet',
            price='2000.00',
            stock=0,
        )
        inactive_type = ProductType.objects.create(name='Insumos inactivos', is_active=False)
        Product.objects.create(
            product_type=inactive_type,
            name='Producto de tipo inactivo',
            brand='Vet',
            price='2000.00',
            stock=4,
        )

        response = self.client.get(f'{self.products_endpoint}available/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['id'] for row in response.data], [available.pk])

    def test_product_list_filters_status(self):
        active = Product.objects.create(
            product_type=self.product_type,
            name='Producto activo',
            brand='Vet',
            price='100.00',
        )
        Product.objects.create(
            product_type=self.product_type,
            name='Producto inactivo',
            brand='Vet',
            price='100.00',
            is_active=False,
        )

        response = self.client.get(self.products_endpoint, {'status': 'active'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([row['id'] for row in response.data], [active.pk])

    def test_product_rejects_negative_stock_and_price(self):
        response = self.client.post(
            self.products_endpoint,
            self.product_payload(quantity=-1, price='-1.00'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('price', response.data)

    def test_product_delete_is_logical(self):
        product = Product.objects.create(
            product_type=self.product_type,
            name='Producto para baja',
            brand='Vet',
            price='150.00',
        )

        response = self.client.delete(f'{self.products_endpoint}{product.pk}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        product.refresh_from_db()
        self.assertFalse(product.is_active)

    def test_type_cannot_be_deactivated_while_active_products_exist(self):
        Product.objects.create(
            product_type=self.product_type,
            name='Producto dependiente',
            brand='Vet',
            price='150.00',
        )

        response = self.client.delete(f'{self.types_endpoint}{self.product_type.pk}/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.product_type.refresh_from_db()
        self.assertTrue(self.product_type.is_active)

    def test_product_type_endpoint_is_separate_from_vaccines(self):
        response = self.client.post(
            self.types_endpoint,
            {'name': 'Instrumental', 'description': 'Instrumental reutilizable'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Instrumental')
