from rest_framework import status
from rest_framework.test import APITestCase

from apps.security.models import User
from .models import Veterinarian


class VeterinarianApiTests(APITestCase):
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
