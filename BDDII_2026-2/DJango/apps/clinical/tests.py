from datetime import timedelta

from django.contrib.auth import get_user_model
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
    vaccine_endpoint = '/api/v1/vaccines/'
    batch_endpoint = '/api/v1/vaccine-batches/'

    def setUp(self):
        admin = get_user_model().objects.create_superuser(
            username='clinical-admin',
            email='clinical-admin@example.com',
            password='test-password',
        )
        self.client.force_authenticate(user=admin)
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

    def test_deleting_consultation_is_logical_and_preserves_prescriptions(self):
        consultation = Consultation.objects.create(
            pet=self.pet,
            veterinarian=self.veterinarian,
            symptoms='Symptoms',
            diagnosis='Diagnosis',
        )
        prescription = Prescription.objects.create(
            consultation=consultation,
            medication_name='Medication',
            dosage='1 tablet',
            frequency='Daily',
            duration_days=5,
        )

        response = self.client.delete(
            f'{self.consultation_endpoint}{consultation.pk}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        consultation.refresh_from_db()
        prescription.refresh_from_db()
        self.assertFalse(consultation.is_active)
        self.assertEqual(prescription.consultation_id, consultation.pk)

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
                'name': self.vaccine.name,
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

    def test_vaccine_application_rejects_non_positive_dose(self):
        batch = self.create_batch(stock_quantity=2)

        response = self.client.post(
            self.application_endpoint,
            {
                'consultation': self.create_consultation().pk,
                'vaccine_batch': batch.pk,
                'name': 'Rabies vaccination',
                'dosage_ml': '0',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dosage_ml', response.data)
        batch.refresh_from_db()
        self.assertEqual(batch.stock_quantity, 2)

    def test_vaccine_catalog_can_be_created_and_updated(self):
        created = self.client.post(
            self.vaccine_endpoint,
            {'name': 'Distemper', 'description': 'Core vaccine'},
            format='json',
        )

        self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
        vaccine = Vaccine.objects.get(pk=created.data['id'])
        self.assertEqual(vaccine.name, 'Distemper')

        updated = self.client.patch(
            f'{self.vaccine_endpoint}{vaccine.pk}/',
            {'is_active': False},
            format='json',
        )

        self.assertEqual(updated.status_code, status.HTTP_200_OK, updated.data)
        vaccine.refresh_from_db()
        self.assertFalse(vaccine.is_active)

    def test_vaccine_batch_can_be_created_and_stock_updated(self):
        created = self.client.post(
            self.batch_endpoint,
            {
                'vaccine': self.vaccine.pk,
                'name': 'Batch A',
                'batch_number': 'batch-api-test',
                'expiration_date': str(timezone.localdate() + timedelta(days=30)),
                'stock_quantity': 10,
            },
            format='json',
        )

        self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
        batch = VaccineBatch.objects.get(pk=created.data['id'])
        self.assertEqual(batch.vaccine_id, self.vaccine.pk)
        self.assertEqual(batch.stock_quantity, 10)

        updated = self.client.patch(
            f'{self.batch_endpoint}{batch.pk}/',
            {'stock_quantity': 7},
            format='json',
        )

        self.assertEqual(updated.status_code, status.HTTP_200_OK, updated.data)
        batch.refresh_from_db()
        self.assertEqual(batch.stock_quantity, 7)

    def test_active_batch_requires_an_active_vaccine(self):
        inactive_vaccine = Vaccine.objects.create(
            name='Inactive vaccine',
            is_active=False,
        )
        response = self.client.post(
            self.batch_endpoint,
            {
                'vaccine': inactive_vaccine.pk,
                'name': 'Inactive parent batch',
                'batch_number': 'batch-inactive-parent',
                'expiration_date': str(timezone.localdate() + timedelta(days=30)),
                'stock_quantity': 5,
                'is_active': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('vaccine', response.data)
        self.assertFalse(
            VaccineBatch.objects.filter(batch_number='batch-inactive-parent').exists()
        )

    def test_vaccine_cannot_be_deactivated_before_its_active_batches(self):
        batch = self.create_batch()

        response = self.client.patch(
            f'{self.vaccine_endpoint}{self.vaccine.pk}/',
            {'is_active': False},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('is_active', response.data)
        self.vaccine.refresh_from_db()
        batch.refresh_from_db()
        self.assertTrue(self.vaccine.is_active)
        self.assertTrue(batch.is_active)

    def test_vaccine_application_requires_batch_vaccine_name(self):
        batch = self.create_batch()
        consultation = self.create_consultation()

        mismatch = self.client.post(
            self.application_endpoint,
            {
                'consultation': consultation.pk,
                'vaccine_batch': batch.pk,
                'name': 'Different vaccine',
                'dosage_ml': '1.00',
            },
            format='json',
        )
        self.assertEqual(mismatch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', mismatch.data)

        derived = self.client.post(
            self.application_endpoint,
            {
                'consultation': consultation.pk,
                'vaccine_batch': batch.pk,
                'dosage_ml': '1.00',
            },
            format='json',
        )
        self.assertEqual(derived.status_code, status.HTTP_201_CREATED, derived.data)
        self.assertEqual(derived.data['name'], self.vaccine.name)
        batch.refresh_from_db()
        self.assertEqual(batch.stock_quantity, 0)

    def test_vaccine_application_rejects_batch_of_inactive_parent_vaccine(self):
        inactive_vaccine = Vaccine.objects.create(
            name='Inactive parent',
            is_active=False,
        )
        batch = self.create_batch(
            vaccine=inactive_vaccine,
            name='Legacy parent batch',
            stock_quantity=3,
        )

        response = self.client.post(
            self.application_endpoint,
            {
                'consultation': self.create_consultation().pk,
                'vaccine_batch': batch.pk,
                'dosage_ml': '1.00',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('vaccine_batch', response.data)
        batch.refresh_from_db()
        self.assertEqual(batch.stock_quantity, 3)

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
