from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.appointment.models import Appointment
from apps.appointment.serializers import AppointmentSerializer
from apps.clinical.models import Consultation
from apps.patient.models import Owner, Pet
from apps.staff.models import Veterinarian


class AppointmentApiTests(APITestCase):
    endpoint = '/api/v1/appointments/'

    def setUp(self):
        admin = get_user_model().objects.create_superuser(
            username='appointment-admin',
            email='appointment-admin@example.com',
            password='test-password',
        )
        self.client.force_authenticate(user=admin)
        owner = Owner.objects.create(
            name='Pet owner',
            doc_type='CC',
            doc_number='appointment-owner-1',
        )
        self.pet = Pet.objects.create(owner=owner, name='Luna')
        self.other_pet = Pet.objects.create(owner=owner, name='Milo')
        self.veterinarian = Veterinarian.objects.create(name='Dr. Vet')
        self.other_veterinarian = Veterinarian.objects.create(name='Dr. Other')

    def appointment_payload(self, **overrides):
        return {
            'pet': self.pet.pk,
            'veterinarian': self.veterinarian.pk,
            'start_time': '2026-10-30T09:00:00-05:00',
            'end_time': '2026-10-30T10:00:00-05:00',
            'reason': 'Annual checkup',
            **overrides,
        }

    def test_create_rejects_end_time_before_start_time(self):
        response = self.client.post(
            self.endpoint,
            self.appointment_payload(end_time='2026-10-30T09:00:00-05:00'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_time', response.data)

    def test_create_requires_active_pet_and_veterinarian(self):
        self.pet.is_active = False
        self.pet.save(update_fields=['is_active'])
        self.veterinarian.is_active = False
        self.veterinarian.save(update_fields=['is_active'])

        response = self.client.post(
            self.endpoint,
            self.appointment_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pet', response.data)
        self.assertIn('veterinarian', response.data)

    def test_create_rejects_unknown_status_with_actionable_error(self):
        response = self.client.post(
            self.endpoint,
            self.appointment_payload(status='WAITING'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('SCHEDULED', str(response.data['status']))

    def test_active_appointments_cannot_overlap_for_same_pet_or_veterinarian(self):
        created = self.client.post(
            self.endpoint,
            self.appointment_payload(),
            format='json',
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)

        same_pet = self.client.post(
            self.endpoint,
            self.appointment_payload(
                veterinarian=self.other_veterinarian.pk,
                start_time='2026-10-30T09:30:00-05:00',
                end_time='2026-10-30T10:30:00-05:00',
            ),
            format='json',
        )
        same_veterinarian = self.client.post(
            self.endpoint,
            self.appointment_payload(
                pet=self.other_pet.pk,
                start_time='2026-10-30T09:30:00-05:00',
                end_time='2026-10-30T10:30:00-05:00',
            ),
            format='json',
        )

        self.assertEqual(same_pet.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(same_veterinarian.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelled_and_completed_appointments_do_not_block_schedule(self):
        for index, appointment_status in enumerate(
            (Appointment.StatusChoices.CANCELLED, Appointment.StatusChoices.COMPLETED)
        ):
            Appointment.objects.create(
                pet=self.pet,
                veterinarian=self.veterinarian,
                start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
                end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
                reason=f'Previous visit {index}',
                status=appointment_status,
            )

        response = self.client.post(
            self.endpoint,
            self.appointment_payload(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_adjacent_appointments_do_not_overlap(self):
        Appointment.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
            reason='Previous visit',
        )

        response = self.client.post(
            self.endpoint,
            self.appointment_payload(
                start_time='2026-10-30T10:00:00-05:00',
                end_time='2026-10-30T11:00:00-05:00',
            ),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_rejects_overlap_with_another_active_appointment(self):
        first = Appointment.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
            reason='First visit',
        )
        second = Appointment.objects.create(
            pet=self.other_pet,
            veterinarian=self.other_veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
            reason='Second visit',
        )

        response = self.client.patch(
            f'{self.endpoint}{second.pk}/',
            {'pet': first.pet_id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        second.refresh_from_db()
        self.assertEqual(second.pet_id, self.other_pet.pk)

    def test_reactivation_rejects_inactive_pet_or_veterinarian(self):
        appointment = Appointment.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
            reason='Cancelled appointment',
            is_active=False,
        )
        self.pet.is_active = False
        self.pet.save(update_fields=['is_active'])

        inactive_pet = self.client.patch(
            f'{self.endpoint}{appointment.pk}/',
            {'is_active': True},
            format='json',
        )
        self.assertEqual(inactive_pet.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pet', inactive_pet.data)

        self.pet.is_active = True
        self.pet.save(update_fields=['is_active'])
        self.veterinarian.is_active = False
        self.veterinarian.save(update_fields=['is_active'])
        inactive_veterinarian = self.client.patch(
            f'{self.endpoint}{appointment.pk}/',
            {'status': Appointment.StatusChoices.CONFIRMED},
            format='json',
        )
        self.assertEqual(
            inactive_veterinarian.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('veterinarian', inactive_veterinarian.data)
        appointment.refresh_from_db()
        self.assertFalse(appointment.is_active)

    def test_reactivation_rechecks_participant_state_when_saving(self):
        appointment = Appointment.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
            reason='Cancelled appointment',
            is_active=False,
        )
        serializer = AppointmentSerializer(
            instance=appointment,
            data={'is_active': True},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        self.pet.is_active = False
        self.pet.save(update_fields=['is_active'])

        with self.assertRaisesMessage(ValidationError, 'Select an active pet.'):
            serializer.save()

        appointment.refresh_from_db()
        self.assertFalse(appointment.is_active)

    def test_reactivation_checks_for_schedule_conflicts(self):
        Appointment.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
            reason='Existing appointment',
        )
        cancelled = Appointment.objects.create(
            pet=self.other_pet,
            veterinarian=self.veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:30:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:30:00-05:00'),
            reason='Cancelled appointment',
            is_active=False,
        )

        response = self.client.patch(
            f'{self.endpoint}{cancelled.pk}/',
            {'is_active': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        cancelled.refresh_from_db()
        self.assertFalse(cancelled.is_active)

    def test_deleting_appointment_cancels_logically_and_keeps_payment_history(self):
        from apps.billing.models import Payment

        appointment = Appointment.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            start_time=datetime.fromisoformat('2026-10-30T09:00:00-05:00'),
            end_time=datetime.fromisoformat('2026-10-30T10:00:00-05:00'),
            reason='Consultation appointment',
        )
        consultation = Consultation.objects.create(
            appointment=appointment,
            pet=self.pet,
            veterinarian=self.veterinarian,
            symptoms='Symptoms',
            diagnosis='Diagnosis',
        )
        payment = Payment.objects.create(
            appointment=appointment,
            reference_type='APPOINTMENT',
            reference_id=appointment.pk,
            method=Payment.MethodChoices.CASH,
            amount='25.00',
        )

        response = self.client.delete(
            f'{self.endpoint}{appointment.pk}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        appointment.refresh_from_db()
        payment.refresh_from_db()
        consultation.refresh_from_db()
        self.assertFalse(appointment.is_active)
        self.assertEqual(
            appointment.status,
            Appointment.StatusChoices.CANCELLED,
        )
        self.assertEqual(payment.appointment_id, appointment.pk)
        self.assertEqual(consultation.appointment_id, appointment.pk)
