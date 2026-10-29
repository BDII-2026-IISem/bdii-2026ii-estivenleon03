from rest_framework import status
from rest_framework.test import APITestCase

from apps.patient.models import Owner, Pet


class OwnerApiTests(APITestCase):
    endpoint = '/api/v1/owners/'

    def test_create_owner_maps_frontend_fields_to_model(self):
        response = self.client.post(
            self.endpoint,
            {
                'nombre': 'Daniel José León Acosta',
                'documento': '1123235612',
                'telefono': '3004830087',
                'email': 'daniel@example.com',
                'direccion': 'Manzana B casa 1',
                'status': 'active',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        owner = Owner.objects.get(doc_number='1123235612')
        self.assertEqual(owner.name, 'Daniel José León Acosta')
        self.assertEqual(owner.phone, '3004830087')
        self.assertEqual(owner.address, 'Manzana B casa 1')
        self.assertTrue(owner.is_active)
        self.assertEqual(response.data['nombre'], owner.name)
        self.assertEqual(response.data['documento'], owner.doc_number)

    def test_update_owner_accepts_frontend_field_names(self):
        owner = Owner.objects.create(
            name='Nombre anterior',
            doc_type='CC',
            doc_number='12345678',
        )

        response = self.client.patch(
            f'{self.endpoint}{owner.pk}/',
            {'nombre': 'Nombre actualizado', 'direccion': 'Calle 10'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        owner.refresh_from_db()
        self.assertEqual(owner.name, 'Nombre actualizado')
        self.assertEqual(owner.address, 'Calle 10')

    def test_create_owner_rejects_duplicate_document_with_validation_error(self):
        Owner.objects.create(name='Existente', doc_type='CC', doc_number='12345678')

        response = self.client.post(
            self.endpoint,
            {'nombre': 'Duplicado', 'documento': '12345678'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('documento', response.data)

    def test_delete_owner_is_logical_and_keeps_related_pets(self):
        owner = Owner.objects.create(
            name='Propietario con mascota',
            doc_type='CC',
            doc_number='87654321',
        )
        pet = Pet.objects.create(owner=owner, name='Kira', species='Canino')

        response = self.client.delete(f'{self.endpoint}{owner.pk}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        owner.refresh_from_db()
        pet.refresh_from_db()
        self.assertFalse(owner.is_active)
        self.assertEqual(pet.owner_id, owner.pk)

    def test_owner_can_be_reactivated(self):
        owner = Owner.objects.create(
            name='Propietario inactivo',
            doc_type='CC',
            doc_number='87654322',
            is_active=False,
        )

        response = self.client.patch(
            f'{self.endpoint}{owner.pk}/',
            {'status': 'active'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        owner.refresh_from_db()
        self.assertTrue(owner.is_active)
        self.assertEqual(response.data['status'], 'active')

    def test_permanent_delete_removes_owner_without_pets(self):
        owner = Owner.objects.create(
            name='Propietario sin mascotas',
            doc_type='CC',
            doc_number='87654323',
            is_active=False,
        )

        response = self.client.delete(
            f'{self.endpoint}{owner.pk}/permanent-delete/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Owner.objects.filter(pk=owner.pk).exists())

    def test_permanent_delete_rejects_owner_with_pets(self):
        owner = Owner.objects.create(
            name='Propietario con mascota',
            doc_type='CC',
            doc_number='87654324',
            is_active=False,
        )
        pet = Pet.objects.create(owner=owner, name='Luna', species='Canino')

        response = self.client.delete(
            f'{self.endpoint}{owner.pk}/permanent-delete/'
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        owner.refresh_from_db()
        self.assertFalse(owner.is_active)
        self.assertTrue(Pet.objects.filter(pk=pet.pk, owner=owner).exists())

    def test_permanent_delete_rejects_active_owner(self):
        owner = Owner.objects.create(
            name='Propietario activo',
            doc_type='CC',
            doc_number='87654325',
        )

        response = self.client.delete(
            f'{self.endpoint}{owner.pk}/permanent-delete/'
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Owner.objects.filter(pk=owner.pk, is_active=True).exists())
