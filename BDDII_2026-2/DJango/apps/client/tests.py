from rest_framework.test import APITestCase
from apps.client.models import Client
from apps.common.status import RecordStatus
from apps.common.testing import create_active_user, grant_crud

class ClientApiTests(APITestCase):
    def setUp(self):
        self.user = create_active_user()
        grant_crud(self.user, "/api/clients/", "/api/clients/1/")
        self.client.force_authenticate(user=self.user)

    def test_client_crud_and_soft_delete(self):
        created = self.client.post(
            "/api/clients/",
            {
                "name": "Supermercado Central",
                "email": "contacto@central.test",
                "phone": "555-1234",
                "address": "Calle Principal 123",
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["status"], RecordStatus.INACTIVE)
        pk = created.data["id"]

        listed = self.client.get("/api/clients/")
        self.assertEqual(listed.status_code, 200)

        detail = self.client.get(f"/api/clients/{pk}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["name"], "Supermercado Central")

        updated = self.client.patch(
            f"/api/clients/{pk}/",
            {"status": "active"},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["status"], RecordStatus.ACTIVE)

        deleted = self.client.delete(f"/api/clients/{pk}/")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(Client.objects.get(pk=pk).status, RecordStatus.INACTIVE)
