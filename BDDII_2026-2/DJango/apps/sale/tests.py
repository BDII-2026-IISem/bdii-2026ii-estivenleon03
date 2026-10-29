from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.patient.models import Owner, Pet
from apps.product.models import Product, ProductType
from .models import Sale, SalePayment


class SaleWorkflowApiTests(APITestCase):
    endpoint = '/api/v1/sales/'

    def setUp(self):
        self.owner = Owner.objects.create(
            doc_type='CC',
            doc_number='SALE-OWNER-1',
            name='Ana López',
        )
        self.other_owner = Owner.objects.create(
            doc_type='CC',
            doc_number='SALE-OWNER-2',
            name='Luis Pérez',
        )
        self.pet = Pet.objects.create(owner=self.owner, name='Luna')
        self.product_type = ProductType.objects.create(name='Medicamentos')
        self.product = Product.objects.create(
            product_type=self.product_type,
            name='Antiparasitario',
            brand='Vet',
            price=Decimal('100.00'),
            stock=10,
        )

    def payload(self, **overrides):
        return {
            'clientId': self.owner.pk,
            'petId': self.pet.pk,
            'saleDate': '2026-10-29T10:00:00-05:00',
            'discounts': '0.00',
            'items': [{'productId': self.product.pk, 'quantity': 2}],
            **overrides,
        }

    def test_create_snapshots_prices_calculates_totals_and_records_initial_tender(self):
        response = self.client.post(
            self.endpoint,
            self.payload(paymentMethod='CASH', paymentAmount='50.00'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['client'], self.owner.pk)
        self.assertEqual(response.data['clientName'], self.owner.name)
        self.assertEqual(response.data['pet'], self.pet.pk)
        self.assertEqual(response.data['petName'], self.pet.name)
        self.assertEqual(response.data['subtotal'], '200.00')
        self.assertEqual(response.data['tax'], '38.00')
        self.assertEqual(response.data['total'], '238.00')
        self.assertEqual(response.data['status'], 'active')
        self.assertEqual(response.data['paidAmount'], '50.00')
        self.assertEqual(response.data['balanceDue'], '188.00')
        self.assertEqual(response.data['paymentStatus'], 'PARTIAL')
        self.assertEqual(response.data['items'], [{
            'productId': self.product.pk,
            'productName': 'Antiparasitario',
            'quantity': 2,
            'unitPrice': '100.00',
            'lineTotal': '200.00',
        }])
        self.assertEqual(response.data['payments'][0]['method'], 'CASH')
        self.assertEqual(response.data['payments'][0]['amount'], '50.00')
        self.assertEqual(response.data['payments'][0]['status'], 'PAID')

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        sale = Sale.objects.get(pk=response.data['id'])
        self.assertEqual(sale.items.get().unit_price, Decimal('100.00'))
        self.assertEqual(sale.payments.count(), 1)

    def test_create_without_pet_or_payment_is_supported(self):
        payload = self.payload()
        payload.pop('petId')

        response = self.client.post(self.endpoint, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIsNone(response.data['pet'])
        self.assertEqual(response.data['payments'], [])
        self.assertEqual(response.data['paidAmount'], '0.00')
        self.assertEqual(response.data['balanceDue'], '238.00')
        self.assertEqual(response.data['paymentStatus'], 'PENDING')

    def test_create_accepts_explicit_null_optional_initial_payment(self):
        response = self.client.post(
            self.endpoint,
            self.payload(paymentMethod=None, paymentAmount=None),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['payments'], [])
        self.assertEqual(response.data['paidAmount'], '0.00')
        self.assertEqual(response.data['balanceDue'], '238.00')
        self.assertEqual(SalePayment.objects.count(), 0)

    def test_rejects_mismatched_pet_empty_items_and_invalid_discount(self):
        cases = [
            (self.payload(clientId=self.other_owner.pk), 'petId'),
            (self.payload(items=[]), 'items'),
            (self.payload(discounts='201.00'), 'discounts'),
        ]
        for payload, field in cases:
            with self.subTest(field=field):
                response = self.client.post(self.endpoint, payload, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                self.assertFalse(Sale.objects.exists())
                self.product.refresh_from_db()
                self.assertEqual(self.product.stock, 10)

    def test_rejects_inactive_or_insufficient_product_without_partial_sale(self):
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])
        inactive_response = self.client.post(
            self.endpoint,
            self.payload(),
            format='json',
        )
        self.assertEqual(inactive_response.status_code, status.HTTP_400_BAD_REQUEST)

        self.product.is_active = True
        self.product.stock = 1
        self.product.save(update_fields=['is_active', 'stock'])
        stock_response = self.client.post(
            self.endpoint,
            self.payload(),
            format='json',
        )
        self.assertEqual(stock_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Sale.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

    def test_initial_tender_requires_both_fields_and_cannot_exceed_total(self):
        for values in (
            {'paymentMethod': 'CASH'},
            {'paymentAmount': '10.00'},
            {'paymentMethod': 'CASH', 'paymentAmount': '300.00'},
            {'paymentMethod': 'OTHER', 'paymentAmount': '10.00'},
            {'paymentMethod': 'CASH', 'paymentAmount': '0.00'},
        ):
            with self.subTest(values=values):
                response = self.client.post(
                    self.endpoint,
                    self.payload(**values),
                    format='json',
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertFalse(Sale.objects.exists())
                self.product.refresh_from_db()
                self.assertEqual(self.product.stock, 10)

    def test_follow_up_payments_cannot_exceed_balance_and_can_settle_sale(self):
        created = self.client.post(
            self.endpoint,
            self.payload(paymentMethod='CASH', paymentAmount='50.00'),
            format='json',
        )
        sale_id = created.data['id']
        payment_url = f'{self.endpoint}{sale_id}/payments/'

        partial = self.client.post(
            payment_url,
            {'method': 'TRANSFER', 'amount': '100.00'},
            format='json',
        )
        self.assertEqual(partial.status_code, status.HTTP_201_CREATED, partial.data)
        self.assertEqual(partial.data['paidAmount'], '150.00')
        self.assertEqual(partial.data['balanceDue'], '88.00')
        self.assertEqual(partial.data['paymentStatus'], 'PARTIAL')
        self.assertEqual(len(partial.data['payments']), 2)

        settled = self.client.post(
            payment_url,
            {'method': 'CREDIT_CARD', 'amount': '88.00'},
            format='json',
        )
        self.assertEqual(settled.status_code, status.HTTP_201_CREATED, settled.data)
        self.assertEqual(settled.data['paidAmount'], '238.00')
        self.assertEqual(settled.data['balanceDue'], '0.00')
        self.assertEqual(settled.data['paymentStatus'], 'PAID')

        overpayment = self.client.post(
            payment_url,
            {'method': 'CASH', 'amount': '0.01'},
            format='json',
        )
        self.assertEqual(overpayment.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', overpayment.data)
        self.assertEqual(SalePayment.objects.filter(sale_id=sale_id).count(), 3)

    def test_follow_up_payment_is_rejected_for_voided_sale(self):
        created = self.client.post(self.endpoint, self.payload(), format='json')
        sale_id = created.data['id']
        self.client.delete(f'{self.endpoint}{sale_id}/')

        response = self.client.post(
            f'{self.endpoint}{sale_id}/payments/',
            {'method': 'CASH', 'amount': '10.00'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(SalePayment.objects.filter(sale_id=sale_id).exists())

    def test_delete_voids_sale_restores_stock_and_retains_cancelled_payment(self):
        created = self.client.post(
            self.endpoint,
            self.payload(paymentMethod='TRANSFER', paymentAmount='25.00'),
            format='json',
        )
        sale_id = created.data['id']

        response = self.client.delete(f'{self.endpoint}{sale_id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
        sale = Sale.objects.get(pk=sale_id)
        self.assertFalse(sale.is_active)
        payment = SalePayment.objects.get(sale=sale)
        self.assertEqual(payment.status, SalePayment.StatusChoices.CANCELLED)
        self.assertEqual(sale.payments.count(), 1)

        detail = self.client.get(f'{self.endpoint}{sale_id}/')
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data['status'], 'inactive')
        self.assertEqual(detail.data['payments'][0]['status'], 'CANCELLED')
        self.assertEqual(detail.data['paidAmount'], '0.00')
        self.assertEqual(detail.data['balanceDue'], '0.00')
        self.assertEqual(detail.data['paymentStatus'], 'CANCELLED')

        repeated_delete = self.client.delete(f'{self.endpoint}{sale_id}/')
        self.assertEqual(repeated_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(SalePayment.objects.filter(sale_id=sale_id).count(), 1)
