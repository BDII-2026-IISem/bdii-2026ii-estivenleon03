from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.testing import PASSWORD, create_active_user, grant
from apps.security.models import Permission, Role, RolePermission, UserRole

User = get_user_model()


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.user = create_active_user()

    def test_login_accepts_username_or_email(self):
        by_username = self.client.post(
            "/api/v1/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(by_username.status_code, status.HTTP_200_OK)
        self.assertIn("access", by_username.data)
        self.assertIn("refresh", by_username.data)
        self.assertNotIn("password", by_username.data)

        by_email = self.client.post(
            "/api/v1/auth/login/",
            {"email": "ANA@STORELAB.TEST", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(by_email.status_code, status.HTTP_200_OK)

    def test_inactive_user_and_bad_password_are_rejected(self):
        bad_password = self.client.post(
            "/api/v1/auth/login/",
            {"username": "ana", "password": "incorrect"},
            format="json",
        )
        self.assertEqual(bad_password.status_code, status.HTTP_401_UNAUTHORIZED)

        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        inactive = self.client.post(
            "/api/v1/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(inactive.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_tokens_and_rejects_reuse(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        first = login.data["refresh"]

        rotated = self.client.post(
            "/api/v1/auth/refresh/",
            {"refresh": first},
            format="json",
        )
        self.assertEqual(rotated.status_code, status.HTTP_200_OK)
        second = rotated.data["refresh"]
        self.assertNotEqual(first, second)

        reused = self.client.post(
            "/api/v1/auth/refresh/",
            {"refresh": first},
            format="json",
        )
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        raw_refresh = login.data["refresh"]

        logout = self.client.post(
            "/api/v1/auth/logout/",
            {"refresh": raw_refresh},
            format="json",
        )
        self.assertEqual(logout.status_code, status.HTTP_204_NO_CONTENT)

        refresh = self.client.post(
            "/api/v1/auth/refresh/",
            {"refresh": raw_refresh},
            format="json",
        )
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication_and_updates_profile_fields(self):
        anonymous = self.client.get("/api/v1/auth/profile/")
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

        login = self.client.post(
            "/api/v1/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        profile = self.client.get("/api/v1/auth/profile/")
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data["username"], "ana")

        updated = self.client.patch(
            "/api/v1/auth/profile/",
            {"firstName": "Ana", "avatar": "https://example.test/ana.png"},
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ana")
        self.assertEqual(updated.data["avatar"], "https://example.test/ana.png")


class RbacApiTests(APITestCase):
    def setUp(self):
        self.admin = create_active_user(
            username="admin",
            email="admin@storelab.test",
        )
        self.admin.is_staff = True
        self.admin.save(update_fields=["is_staff"])
        self.client.force_authenticate(user=self.admin)

    def test_user_role_resource_and_permission_flow(self):
        user_response = self.client.post(
            "/api/v1/users/",
            {
                "username": "bodega",
                "email": "bodega@storelab.test",
                "password": PASSWORD,
                "avatar": "https://example.test/bodega.png",
                "status": "active",
            },
            format="json",
        )
        self.assertEqual(user_response.status_code, status.HTTP_201_CREATED)
        user_id = user_response.data["id"]
        self.assertNotIn("password", user_response.data)
        self.assertEqual(user_response.data["avatar"], "https://example.test/bodega.png")

        role_response = self.client.post(
            "/api/v1/roles/",
            {"name": "BODEGA", "description": "Inventario", "status": "active"},
            format="json",
        )
        self.assertEqual(role_response.status_code, status.HTTP_201_CREATED)
        role_id = role_response.data["id"]

        assignment_response = self.client.post(
            "/api/v1/user-roles/",
            {"userId": user_id, "roleId": role_id, "status": "active"},
            format="json",
        )
        self.assertEqual(assignment_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(assignment_response.data["userId"], user_id)
        self.assertIsNone(UserRole.objects.get(pk=assignment_response.data["id"]).user_id)

        resource_response = self.client.post(
            "/api/v1/permissions/",
            {
                "method": "GET",
                "path": "/api/owners/",
                "description": "Consultar propietarios",
                "status": "active",
            },
            format="json",
        )
        self.assertEqual(resource_response.status_code, status.HTTP_201_CREATED)
        permission_id = resource_response.data["id"]

        grant_response = self.client.post(
            "/api/v1/role-permissions/",
            {
                "roleId": role_id,
                "resourceId": permission_id,
                "status": "active",
            },
            format="json",
        )
        self.assertEqual(grant_response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(pk=user_id)
        self.client.force_authenticate(user=user)
        denied = self.client.post(
            "/api/v1/owners/",
            {"name": "No autorizado"},
            format="json",
        )
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

        allowed = self.client.get("/api/v1/owners/")
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

        effective = self.client.get("/api/v1/auth/permissions/")
        self.assertEqual(effective.status_code, status.HTTP_200_OK)
        self.assertEqual(len(effective.data["permissions"]), 1)
        self.assertEqual(effective.data["permissions"][0]["roleName"], "BODEGA")

    def test_missing_grant_denies_authenticated_user(self):
        user = create_active_user(
            username="no-role",
            email="unassigned@storelab.test",
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/v1/owners/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_role_assignment_or_permission_denies_access(self):
        user = create_active_user(
            username="limited",
            email="limited@storelab.test",
        )
        role = grant(user, "GET", "/api/owners/")
        self.client.force_authenticate(user=user)

        self.assertEqual(self.client.get("/api/v1/owners/").status_code, status.HTTP_200_OK)

        role.is_active = False
        role.save(update_fields=["is_active"])
        self.assertEqual(self.client.get("/api/v1/owners/").status_code, status.HTTP_403_FORBIDDEN)
        role.is_active = True
        role.save(update_fields=["is_active"])

        assignment = UserRole.objects.get(auth_user=user, role=role)
        assignment.is_active = False
        assignment.save(update_fields=["is_active"])
        self.assertEqual(self.client.get("/api/v1/owners/").status_code, status.HTTP_403_FORBIDDEN)
        assignment.is_active = True
        assignment.save(update_fields=["is_active"])

        grant_record = RolePermission.objects.get(role=role)
        grant_record.is_active = False
        grant_record.save(update_fields=["is_active"])
        self.assertEqual(self.client.get("/api/v1/owners/").status_code, status.HTTP_403_FORBIDDEN)

        permission = Permission.objects.get(pk=grant_record.permission_id)
        grant_record.is_active = True
        grant_record.save(update_fields=["is_active"])
        permission.is_active = False
        permission.save(update_fields=["is_active"])
        self.assertEqual(self.client.get("/api/v1/owners/").status_code, status.HTTP_403_FORBIDDEN)
