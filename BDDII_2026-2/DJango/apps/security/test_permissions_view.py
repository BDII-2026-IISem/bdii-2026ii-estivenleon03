from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Permission, Role, RolePermission, User, UserRole


class EffectivePermissionsApiTests(APITestCase):
    endpoint = '/api/v1/auth/permissions/'

    def test_returns_only_permissions_granted_to_matching_rbac_user(self):
        auth_user = get_user_model().objects.create_user(
            username='vet-login',
            email='vet@example.com',
            password='test-password',
        )
        rbac_user = User.objects.create(
            name='Veterinaria',
            email='vet@example.com',
            password_hash='unused',
        )
        role = Role.objects.create(name='VETERINARIAN')
        permission = Permission.objects.create(
            resource='/api/v1/consultations',
            http_method='GET',
        )
        UserRole.objects.create(user=rbac_user, role=role)
        RolePermission.objects.create(role=role, permission=permission)
        self.client.force_authenticate(user=auth_user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['permissions'], [{
            'method': 'GET',
            'path': '/api/v1/consultations',
            'roleId': role.pk,
            'roleName': role.name,
        }])

    def test_authenticated_user_without_rbac_mapping_receives_no_permissions(self):
        auth_user = get_user_model().objects.create_user(
            username='no-role',
            email='unassigned@example.com',
            password='test-password',
        )
        self.client.force_authenticate(user=auth_user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'permissions': []})

    def test_seed_registers_resolvable_templates_and_is_idempotent(self):
        call_command('seed_rbac', stdout=StringIO())
        first_count = Permission.objects.count()

        call_command('seed_rbac', stdout=StringIO())

        self.assertEqual(Permission.objects.count(), first_count)
        self.assertTrue(Permission.objects.filter(
            http_method='GET',
            resource='/api/v1/owners',
        ).exists())
        self.assertTrue(Permission.objects.filter(
            http_method='GET',
            resource='/api/v1/owners/:id',
        ).exists())
        self.assertTrue(Permission.objects.filter(
            http_method='POST',
            resource='/api/v1/sales/:id/payments',
        ).exists())
        self.assertFalse(
            Permission.objects.filter(resource__contains='(?P').exists()
        )
