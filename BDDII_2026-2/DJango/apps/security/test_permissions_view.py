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
        role = Role.objects.create(name='VETERINARIO')
        permission = Permission.objects.create(
            resource='/api/v1/consultations',
            http_method='GET',
        )
        UserRole.objects.create(
            user=rbac_user,
            auth_user=auth_user,
            role=role,
        )
        RolePermission.objects.create(role=role, permission=permission)
        self.client.force_authenticate(user=auth_user)

        response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['permissions'], [{
            'method': 'GET',
            'path': 'api/v1/consultations/',
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
            resource='api/v1/owners/',
        ).exists())
        self.assertTrue(Permission.objects.filter(
            http_method='GET',
            resource='api/v1/owners/<int:pk>/',
        ).exists())
        self.assertTrue(Permission.objects.filter(
            http_method='POST',
            resource='api/v1/sales/<int:pk>/payments/',
        ).exists())
        audit_permissions = Permission.objects.filter(
            resource__in=(
                'api/v1/payment-audits/',
                'api/v1/payment-audits/<int:pk>/',
            )
        )
        self.assertTrue(audit_permissions.filter(http_method='GET').exists())
        self.assertTrue(
            RolePermission.objects.filter(
                role__name='ADMIN',
                permission__in=audit_permissions,
                permission__http_method='GET',
            ).exists()
        )
        self.assertFalse(
            RolePermission.objects.filter(
                role__name='ADMIN',
                permission__in=audit_permissions,
            ).exclude(permission__http_method='GET').exists()
        )
        self.assertFalse(
            Permission.objects.filter(resource__contains='(?P').exists()
        )

    def test_seed_creates_and_reactivates_all_assignable_roles(self):
        Role.objects.create(name="ADMIN", is_active=False)
        Role.objects.create(name="RECEPCIONISTA", is_active=False)

        call_command("seed_rbac", stdout=StringIO())

        self.assertEqual(
            set(
                Role.objects.filter(is_active=True).values_list("name", flat=True)
            ),
            {"ADMIN", "VETERINARIO", "RECEPCIONISTA", "PROPIETARIO"},
        )

    def test_seed_applies_crud_matrix_for_each_application_role(self):
        veterinarian_role = Role.objects.create(name="VETERINARIO")
        stale_permission = Permission.objects.create(
            http_method="DELETE",
            resource="/api/v1/consultations/:id",
        )
        RolePermission.objects.create(
            role=veterinarian_role,
            permission=stale_permission,
        )

        call_command("seed_rbac", stdout=StringIO())

        def grants(role_name):
            return set(
                RolePermission.objects.filter(role__name=role_name)
                .values_list("permission__http_method", "permission__resource")
            )

        veterinarian = grants("VETERINARIO")
        self.assertIn(("POST", "api/v1/owners/"), veterinarian)
        self.assertIn(("PATCH", "api/v1/pets/<int:pk>/"), veterinarian)
        self.assertIn(("PATCH", "api/v1/consultations/<int:pk>/"), veterinarian)
        self.assertIn(("PATCH", "api/v1/products/<int:pk>/"), veterinarian)
        self.assertIn(("GET", "api/v1/sales/"), veterinarian)
        self.assertNotIn(("DELETE", "api/v1/consultations/<int:pk>/"), veterinarian)
        self.assertNotIn(("POST", "api/v1/products/"), veterinarian)
        self.assertFalse(
            RolePermission.objects.filter(
                role=veterinarian_role,
                permission=stale_permission,
            ).exists()
        )

        receptionist = grants("RECEPCIONISTA")
        self.assertIn(("POST", "api/v1/appointments/"), receptionist)
        self.assertIn(("DELETE", "api/v1/appointments/<int:pk>/"), receptionist)
        self.assertIn(("POST", "api/v1/sales/"), receptionist)
        self.assertIn(("GET", "api/v1/consultations/"), receptionist)
        self.assertNotIn(("DELETE", "api/v1/sales/<int:pk>/"), receptionist)
        self.assertNotIn(("PATCH", "api/v1/consultations/<int:pk>/"), receptionist)

        owner = grants("PROPIETARIO")
        self.assertIn(("GET", "api/v1/owners/"), owner)
        self.assertIn(("PATCH", "api/v1/owners/<int:pk>/"), owner)
        self.assertNotIn(("POST", "api/v1/owners/"), owner)
        self.assertIn(("GET", "api/v1/pets/"), owner)
        self.assertNotIn(("PATCH", "api/v1/pets/<int:pk>/"), owner)
        self.assertIn(("POST", "api/v1/appointments/"), owner)
        self.assertIn(("DELETE", "api/v1/appointments/<int:pk>/"), owner)
        self.assertNotIn(("PATCH", "api/v1/appointments/<int:pk>/"), owner)
        self.assertIn(("GET", "api/v1/prescriptions/"), owner)
        self.assertNotIn(("GET", "api/v1/users/"), owner)

    def test_seed_can_assign_the_admin_role_to_a_django_user(self):
        auth_user = get_user_model().objects.create_user(
            username='bootstrap-admin',
            email='bootstrap@example.com',
            password='test-password',
        )

        call_command(
            'seed_rbac',
            username=auth_user.username,
            stdout=StringIO(),
        )

        self.assertTrue(
            UserRole.objects.filter(
                auth_user=auth_user,
                role__name='ADMIN',
                is_active=True,
            ).exists()
        )
