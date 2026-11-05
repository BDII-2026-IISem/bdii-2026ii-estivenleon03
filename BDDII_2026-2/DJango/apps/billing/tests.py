from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from apps.appointment.models import Appointment
from apps.billing.models import Payment, PaymentAudit
from apps.billing.serializers import PaymentSerializer
from apps.common.testing import create_active_user, grant
from apps.patient.models import Owner, Pet
from apps.staff.models import Veterinarian


class PaymentSerializerTests(APITestCase):
    def test_payment_amount_must_be_positive(self):
        amount = PaymentSerializer().fields['amount']

        with self.assertRaises(ValidationError):
            amount.run_validation('0.00')
        with self.assertRaises(ValidationError):
            amount.run_validation('-1.00')

        self.assertEqual(amount.run_validation('1.25'), Decimal('1.25'))


class AppointmentPaymentApiTests(APITestCase):
    endpoint = '/api/v1/payments/'

    def setUp(self):
        admin = get_user_model().objects.create_superuser(
            username='billing-payment-admin',
            email='billing-payment-admin@example.com',
            password='test-password',
        )
        self.client.force_authenticate(user=admin)
        owner = Owner.objects.create(
            name='Payment owner',
            doc_type='CC',
            doc_number='billing-payment-owner',
        )
        pet = Pet.objects.create(owner=owner, name='Luna')
        veterinarian = Veterinarian.objects.create(name='Dr. Payment')
        self.appointment = Appointment.objects.create(
            pet=pet,
            veterinarian=veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
            reason='Payment API test',
        )

    def payload(self, **overrides):
        return {
            'appointment': self.appointment.pk,
            'reference_type': 'APPOINTMENT',
            'reference_id': self.appointment.pk,
            'method': 'CASH',
            'amount': '25.00',
            'status': 'PAID',
            **overrides,
        }

    def test_create_payment_persists_its_appointment_relationship(self):
        response = self.client.post(self.endpoint, self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(pk=response.data['id'])
        self.assertEqual(payment.appointment_id, self.appointment.pk)
        self.assertEqual(payment.reference_id, self.appointment.pk)
        self.assertEqual(payment.amount, Decimal('25.00'))

    def test_payment_endpoint_rejects_non_positive_amounts(self):
        for amount in ('0.00', '-1.00'):
            response = self.client.post(
                self.endpoint,
                self.payload(amount=amount),
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('amount', response.data)

        self.assertEqual(Payment.objects.count(), 0)

    def test_create_rejects_reference_that_does_not_match_appointment(self):
        response = self.client.post(
            self.endpoint,
            self.payload(reference_id=self.appointment.pk + 100),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reference_id', response.data)
        self.assertEqual(Payment.objects.count(), 0)

    def test_create_rejects_reference_type_for_another_payment_domain(self):
        response = self.client.post(
            self.endpoint,
            self.payload(reference_type='SALE'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reference_type', response.data)
        self.assertEqual(Payment.objects.count(), 0)

    def test_update_cannot_break_appointment_reference_consistency(self):
        payment = Payment.objects.create(
            appointment=self.appointment,
            reference_type='APPOINTMENT',
            reference_id=self.appointment.pk,
            method=Payment.MethodChoices.CASH,
            amount=Decimal('25.00'),
        )

        response = self.client.patch(
            f'{self.endpoint}{payment.pk}/',
            {'reference_id': self.appointment.pk + 100},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        payment.refresh_from_db()
        self.assertEqual(payment.reference_id, self.appointment.pk)

    def test_payment_crud_persists_update_and_delete(self):
        created = self.client.post(self.endpoint, self.payload(), format='json')
        payment_id = created.data['id']

        listed = self.client.get(self.endpoint)
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listed.data), 1)

        updated = self.client.patch(
            f'{self.endpoint}{payment_id}/',
            {'status': 'PENDING', 'method': 'TRANSFER'},
            format='json',
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        payment = Payment.objects.get(pk=payment_id)
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.assertEqual(payment.method, Payment.MethodChoices.TRANSFER)

        deleted = self.client.delete(f'{self.endpoint}{payment_id}/')
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Payment.objects.filter(pk=payment_id).exists())

    def test_payment_permissions_are_checked_per_http_method(self):
        user = create_active_user(
            username='billing-limited-user',
            email='billing-limited@example.com',
        )
        grant(user, 'GET', '/api/v1/payments')
        self.client.force_authenticate(user=user)

        self.assertEqual(
            self.client.get(self.endpoint).status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.post(self.endpoint, self.payload(), format='json').status_code,
            status.HTTP_403_FORBIDDEN,
        )


class PaymentAuditApiTests(APITestCase):
    endpoint = '/api/v1/payment-audits/'

    def setUp(self):
        admin = get_user_model().objects.create_superuser(
            username='billing-audit-admin',
            email='billing-audit-admin@example.com',
            password='test-password',
        )
        self.client.force_authenticate(user=admin)
        self.audit = PaymentAudit.objects.create(
            payment_id=999,
            actionSale=PaymentAudit.ActionChoices.DELETE,
            changed_by='Audit test',
            before_data={'amount': '25.00'},
        )

    def test_audit_history_can_be_listed_and_retrieved(self):
        listed = self.client.get(self.endpoint)
        retrieved = self.client.get(f'{self.endpoint}{self.audit.pk}/')

        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieved.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieved.data['payment_id'], 999)
        self.assertEqual(retrieved.data['actionSale'], 'DELETE')
        self.assertEqual(retrieved.data['before_data'], {'amount': '25.00'})

    def test_audit_history_rejects_all_mutating_methods(self):
        responses = (
            self.client.post(self.endpoint, {'payment_id': 1000}, format='json'),
            self.client.put(
                f'{self.endpoint}{self.audit.pk}/',
                {'changed_by': 'tampered'},
                format='json',
            ),
            self.client.patch(
                f'{self.endpoint}{self.audit.pk}/',
                {'changed_by': 'tampered'},
                format='json',
            ),
            self.client.delete(f'{self.endpoint}{self.audit.pk}/'),
        )

        self.assertTrue(
            all(response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
                for response in responses)
        )
        self.audit.refresh_from_db()
        self.assertEqual(self.audit.changed_by, 'Audit test')
        self.assertEqual(self.audit.actionSale, PaymentAudit.ActionChoices.DELETE)
        self.assertEqual(PaymentAudit.objects.count(), 1)

    def test_audit_history_is_returned_newest_first(self):
        older = PaymentAudit.objects.create(
            payment_id=1001,
            actionSale=PaymentAudit.ActionChoices.INSERT,
            changed_by='Older event',
        )
        newer = PaymentAudit.objects.create(
            payment_id=1002,
            actionSale=PaymentAudit.ActionChoices.UPDATE,
            changed_by='Newer event',
        )

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], newer.pk)
        self.assertEqual(response.data[1]['id'], older.pk)
