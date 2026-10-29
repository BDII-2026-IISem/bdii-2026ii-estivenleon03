from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointment.models import Appointment
from apps.clinical.models import (
    Consultation,
    Prescription,
    Vaccine,
    VaccineApplication,
    VaccineBatch,
)
from apps.patient.models import Owner, Pet
from apps.staff.models import Veterinarian


class ClinicalApiTests(APITestCase):
    consultation_endpoint = '/api/v1/consultations/'
    prescription_endpoint = '/api/v1/prescriptions/'
    application_endpoint = '/api/v1/vaccine-applications/'

    def setUp(self):
        owner = Owner.objects.create(
            name='Clinical patient owner',
            doc_type='CC',
            doc_number='clinical-owner-1',
        )
        self.pet = Pet.objects.create(owner=owner, name='Nube')
        self.other_pet = Pet.objects.create(owner=owner, name='Brisa')
        self.veterinarian = Veterinarian.objects.create(name='Dr. Clinical')
        self.other_veterinarian = Veterinarian.objects.create(name='Dr. Alternate')
        self.appointment = Appointment.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            reason='Consultation',
        )
        self.vaccine = Vaccine.objects.create(name='Rabies')

    def test_consultation_derives_pet_and_veterinarian_from_appointment(self):
        response = self.client.post(
            self.consultation_endpoint,
            {
                'appointment': self.appointment.pk,
                'symptoms': 'No symptoms',
                'diagnosis': 'Healthy',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        consultation = Consultation.objects.get(pk=response.data['id'])
        self.assertEqual(consultation.pet_id, self.pet.pk)
        self.assertEqual(consultation.veterinarian_id, self.veterinarian.pk)

    def test_consultation_rejects_pet_or_veterinarian_mismatching_appointment(self):
        response = self.client.post(
            self.consultation_endpoint,
            {
                'appointment': self.appointment.pk,
                'pet': self.other_pet.pk,
                'veterinarian': self.other_veterinarian.pk,
                'symptoms': 'Symptoms',
                'diagnosis': 'Diagnosis',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pet', response.data)
        self.assertIn('veterinarian', response.data)

    def test_standalone_consultation_remains_supported(self):
        response = self.client.post(
            self.consultation_endpoint,
            {
                'pet': self.other_pet.pk,
                'veterinarian': self.other_veterinarian.pk,
                'symptoms': 'Cough',
                'diagnosis': 'Observation',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        consultation = Consultation.objects.get(pk=response.data['id'])
        self.assertIsNone(consultation.appointment_id)

    def test_prescription_requires_positive_duration_and_nonblank_dosage(self):
        consultation = Consultation.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            symptoms='Symptoms',
            diagnosis='Diagnosis',
        )
        payload = {
            'consultation': consultation.pk,
            'medication_name': 'Medication',
            'dosage': '1 tablet',
            'frequency': 'Twice daily',
            'duration_days': 5,
        }

        negative_duration = self.client.post(
            self.prescription_endpoint,
            {**payload, 'duration_days': 0},
            format='json',
        )
        blank_dosage = self.client.post(
            self.prescription_endpoint,
            {**payload, 'dosage': '   '},
            format='json',
        )

        self.assertEqual(negative_duration.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('duration_days', negative_duration.data)
        self.assertEqual(blank_dosage.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dosage', blank_dosage.data)

    def test_vaccine_application_decrements_one_dose(self):
        batch = self.create_batch(stock_quantity=2)

        response = self.client.post(
            self.application_endpoint,
            {
                'consultation': self.create_consultation().pk,
                'vaccine_batch': batch.pk,
                'name': 'Rabies vaccination',
                'dosage_ml': '1.00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        batch.refresh_from_db()
        self.assertEqual(batch.stock_quantity, 1)
        self.assertTrue(
            VaccineApplication.objects.filter(pk=response.data['id']).exists()
        )

    def test_vaccine_application_rejects_inactive_expired_and_empty_batches(self):
        consultation = self.create_consultation()
        cases = (
            self.create_batch(name='Inactive', is_active=False),
            self.create_batch(
                name='Expired',
                expiration_date=timezone.localdate() - timedelta(days=1),
            ),
            self.create_batch(name='Empty', stock_quantity=0),
        )

        for batch in cases:
            with self.subTest(batch=batch.name):
                response = self.client.post(
                    self.application_endpoint,
                    {
                        'consultation': consultation.pk,
                        'vaccine_batch': batch.pk,
                        'name': 'Vaccination',
                    },
                    format='json',
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('vaccine_batch', response.data)

    def test_vaccine_application_cannot_be_updated_or_deleted(self):
        batch = self.create_batch(stock_quantity=0)
        application = VaccineApplication.objects.create(
            consultation=self.create_consultation(),
            vaccine_batch=batch,
            name='Recorded vaccination',
        )

        update = self.client.patch(
            f'{self.application_endpoint}{application.pk}/',
            {'name': 'Changed vaccination'},
            format='json',
        )
        delete = self.client.delete(f'{self.application_endpoint}{application.pk}/')

        self.assertEqual(update.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        application.refresh_from_db()
        batch.refresh_from_db()
        self.assertEqual(application.name, 'Recorded vaccination')
        self.assertEqual(batch.stock_quantity, 0)

    def create_consultation(self):
        return Consultation.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            symptoms='Symptoms',
            diagnosis='Diagnosis',
        )

    def create_batch(self, name='Standard', **overrides):
        values = {
            'vaccine': self.vaccine,
            'name': name,
            'batch_number': f'batch-{name.lower()}',
            'expiration_date': timezone.localdate() + timedelta(days=10),
            'stock_quantity': 1,
        }
        values.update(overrides)
        return VaccineBatch.objects.create(**values)
