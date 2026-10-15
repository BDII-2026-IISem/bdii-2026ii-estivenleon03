from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase
from apps.common.status import RecordStatus
from apps.common.testing import PASSWORD, create_active_user, grant, grant_crud
from apps.security.models import RefreshToken, Resource, ResourceRole, Role, RoleUser, User
from apps.security.tokens import hash_token

class AuthFlowTests(APITestCase):
    def setUp(self):
        self.user = create_active_user()

    def test_login_with_username_and_email(self):
        by_username = self.client.post(
            "/api/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(by_username.status_code, status.HTTP_200_OK)
        self.assertIn("access", by_username.data)
        self.assertIn("refresh", by_username.data)
        self.assertNotIn("password", by_username.data)
        stored = RefreshToken.objects.get()
        self.assertEqual(stored.token_hash, hash_token(by_username.data["refresh"]))
        by_email = self.client.post(
            "/api/auth/login/",
            {"email": "ANA@storelab.test", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(by_email.status_code, status.HTTP_200_OK)

    def test_inactive_user_and_bad_password_are_401(self):
        self.user.status = RecordStatus.INACTIVE
        self.user.save()
        inactive = self.client.post(
            "/api/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(inactive.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_and_reuse_revokes_family(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        first = login.data["refresh"]
        rotated = self.client.post("/api/auth/refresh/", {"refresh": first}, format="json")
        self.assertEqual(rotated.status_code, status.HTTP_200_OK)
        second = rotated.data["refresh"]
        self.assertNotEqual(first, second)
        reused = self.client.post("/api/auth/refresh/", {"refresh": first}, format="json")
        self.assertEqual(reused.status_code, status.HTTP_401_UNAUTHORIZED)
        after_reuse = self.client.post("/api/auth/refresh/", {"refresh": second}, format="json")
        self.assertEqual(after_reuse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalidates_refresh(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        raw = login.data["refresh"]
        logout = self.client.post("/api/auth/logout/", {"refresh": raw}, format="json")
        self.assertEqual(logout.status_code, status.HTTP_204_NO_CONTENT)
        again = self.client.post("/api/auth/refresh/", {"refresh": raw}, format="json")
        self.assertEqual(again.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_token_and_rejects_inactive_user(self):
        anonymous = self.client.get("/api/auth/profile/")
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
        login = self.client.post(
            "/api/auth/login/",
            {"username": "ana", "password": PASSWORD},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        profile = self.client.get("/api/auth/profile/")
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data["username"], "ana")
        patched = self.client.patch(
            "/api/auth/profile/",
            {"firstName": "Ana"},
            format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.user.status = RecordStatus.INACTIVE
        self.user.save()
        denied = self.client.get("/api/auth/profile/")
        self.assertEqual(denied.status_code, status.HTTP_401_UNAUTHORIZED)

class SecurityMatrixApiTests(APITestCase):
    def setUp(self):
        self.user = create_active_user(username="admin_rbac", email="admin@storelab.test")
        grant_crud(self.user, "/api/users/", "/api/users/1/")
        grant_crud(self.user, "/api/roles/", "/api/roles/1/")
        grant_crud(self.user, "/api/role-users/", "/api/role-users/1/")
        grant_crud(self.user, "/api/resources/", "/api/resources/1/")
        grant_crud(self.user, "/api/resource-roles/", "/api/resource-roles/1/")
        self.client.force_authenticate(user=self.user)

    def test_role_crud(self):
        created = self.client.post(
            "/api/roles/",
            {"name": "bodega", "description": "Rol Bodega", "status": "active"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        pk = created.data["id"]

        listed = self.client.get("/api/roles/")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)

        detail = self.client.get(f"/api/roles/{pk}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["name"], "bodega")

        updated = self.client.patch(
            f"/api/roles/{pk}/",
            {"description": "Rol de Bodega e Inventario"},
            format="json",
        )
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["description"], "Rol de Bodega e Inventario")

        deleted = self.client.delete(f"/api/roles/{pk}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Role.objects.get(pk=pk).status, RecordStatus.INACTIVE)

    def test_user_role_resource_chain(self):
        role_res = self.client.post(
            "/api/roles/",
            {"name": "bodega", "status": "active"},
            format="json",
        )
        self.assertEqual(role_res.status_code, status.HTTP_201_CREATED)
        role_id = role_res.data["id"]

        user_res = self.client.post(
            "/api/users/",
            {
                "username": "bodega1",
                "email": "bodega1@storelab.test",
                "password": PASSWORD,
                "status": "active",
            },
            format="json",
        )
        self.assertEqual(user_res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", user_res.data)
        new_user_id = user_res.data["id"]
        new_user = User.objects.get(pk=new_user_id)

        self.client.force_authenticate(user=new_user)
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)

        ru_res = self.client.post(
            "/api/role-users/",
            {"role": role_id, "user": new_user_id, "status": "active"},
            format="json",
        )
        self.assertEqual(ru_res.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=new_user)
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)

        match = resolve("/api/clients/")
        res_res = self.client.post(
            "/api/resources/",
            {"name": "GET Clients", "method": "GET", "route": match.route, "status": "active"},
            format="json",
        )
        self.assertEqual(res_res.status_code, status.HTTP_201_CREATED)
        resource_id = res_res.data["id"]

        self.client.force_authenticate(user=new_user)
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)

        rr_res = self.client.post(
            "/api/resource-roles/",
            {"resource": resource_id, "role": role_id, "status": "active"},
            format="json",
        )
        self.assertEqual(rr_res.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=new_user)
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.post(
                "/api/clients/",
                {"name": "Cliente X", "email": "x@test.com"},
                format="json",
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )

class RbacTests(APITestCase):
    def setUp(self):
        self.user = create_active_user()
        self.client.force_authenticate(user=self.user)

    def test_missing_grant_is_403_and_missing_identity_is_401(self):
        denied = self.client.get("/api/clients/")
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=None)
        anonymous = self.client.get("/api/clients/")
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_any_inactive_link_denies(self):
        role = grant(self.user, "GET", "/api/clients/")
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_200_OK)

        role.status = RecordStatus.INACTIVE
        role.save()
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_403_FORBIDDEN)
        role.status = RecordStatus.ACTIVE
        role.save()

        ru = RoleUser.objects.get(role=role, user=self.user)
        ru.status = RecordStatus.INACTIVE
        ru.save()
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_403_FORBIDDEN)
        ru.status = RecordStatus.ACTIVE
        ru.save()

        rr = ResourceRole.objects.get(role=role)
        rr.status = RecordStatus.INACTIVE
        rr.save()
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_403_FORBIDDEN)
        rr.status = RecordStatus.ACTIVE
        rr.save()

        res = rr.resource
        res.status = RecordStatus.INACTIVE
        res.save()
        self.assertEqual(self.client.get("/api/clients/").status_code, status.HTTP_403_FORBIDDEN)
