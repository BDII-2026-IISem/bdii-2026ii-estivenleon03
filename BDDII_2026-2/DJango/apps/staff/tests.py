from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from apps.security.models import User
from .models import Veterinarian


class VeterinarianApiTests(APITestCase):
    def setUp(self):
        admin = get_user_model().objects.create_superuser(
            username='staff-admin',
            email='staff-admin@example.com',
            password='test-password',
        )
        self.client.force_authenticate(user=admin)

    def test_list_serializes_linked_security_user_without_exposing_password(self):
        user = User.objects.create(
            name='Dra. Laura Méndez',
            email='laura.vet@example.com',
            password_hash='not-a-real-password',
        )
        Veterinarian.objects.create(
            user=user,
            name='Dra. Laura Méndez',
            license_number='VET-TEST-1',
        )

        response = self.client.get('/api/v1/veterinarians/')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        details = response.data[0]['user_details']
        self.assertEqual(details, {
            'id': user.pk,
            'name': user.name,
            'email': user.email,
        })
        self.assertNotIn('password_hash', details)

    def test_create_and_update_veterinarian_profile(self):
        created = self.client.post(
            '/api/v1/veterinarians/',
            {
                'name': 'Dr. Mateo Ríos',
                'license_number': 'VET-TEST-2',
                'description': 'Medicina general',
                'is_active': True,
            },
            format='json',
        )

        self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
        veterinarian = Veterinarian.objects.get(pk=created.data['id'])
        self.assertEqual(veterinarian.name, 'Dr. Mateo Ríos')

        updated = self.client.patch(
            f"/api/v1/veterinarians/{veterinarian.pk}/",
            {'is_active': False},
            format='json',
        )

        self.assertEqual(updated.status_code, status.HTTP_200_OK, updated.data)
        veterinarian.refresh_from_db()
        self.assertFalse(veterinarian.is_active)

    def test_list_includes_canonical_auth_user_details(self):
        auth_user = get_user_model().objects.create_user(
            username='vet-canonical',
            email='canonical.vet@example.com',
            first_name='Laura',
            last_name='Méndez',
            password='test-password',
        )
        veterinarian = Veterinarian.objects.create(
            auth_user=auth_user,
            name='Dra. Laura Méndez',
        )

        response = self.client.get('/api/v1/veterinarians/')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        data = next(row for row in response.data if row['id'] == veterinarian.pk)
        self.assertEqual(
            data['auth_user_details'],
            {
                'id': auth_user.pk,
                'first_name': 'Laura',
                'last_name': 'Méndez',
                'email': 'canonical.vet@example.com',
            },
        )

    def test_veterinarian_can_be_linked_to_active_auth_user(self):
        auth_user = get_user_model().objects.create_user(
            username='vet-linked',
            email='linked.vet@example.com',
            password='test-password',
        )

        response = self.client.post(
            '/api/v1/veterinarians/',
            {
                'name': 'Dra. Vinculada',
                'auth_user': auth_user.pk,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        veterinarian = Veterinarian.objects.get(pk=response.data['id'])
        self.assertEqual(veterinarian.auth_user_id, auth_user.pk)
        self.assertEqual(response.data['auth_user'], auth_user.pk)
        self.assertEqual(
            response.data['auth_user_details']['email'],
            auth_user.email,
        )

    def test_veterinarian_account_is_unique_and_must_be_active(self):
        auth_user = get_user_model().objects.create_user(
            username='vet-unique',
            email='unique.vet@example.com',
            password='test-password',
        )
        Veterinarian.objects.create(auth_user=auth_user, name='Existing')

        duplicate = self.client.post(
            '/api/v1/veterinarians/',
            {'name': 'Duplicate', 'auth_user': auth_user.pk},
            format='json',
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('auth_user', duplicate.data)

        inactive_user = get_user_model().objects.create_user(
            username='vet-inactive',
            email='inactive.vet@example.com',
            password='test-password',
            is_active=False,
        )
        inactive = self.client.post(
            '/api/v1/veterinarians/',
            {'name': 'Inactive', 'auth_user': inactive_user.pk},
            format='json',
        )
        self.assertEqual(inactive.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('auth_user', inactive.data)
