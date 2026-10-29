from datetime import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointment.models import Appointment
from apps.patient.models import Owner, Pet
from apps.staff.models import Veterinarian


class AppointmentApiTests(APITestCase):
    endpoint = '/api/v1/appointments/'

    def setUp(self):
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
