from decimal import Decimal
from django.db.models.deletion import RestrictedError
from rest_framework.test import APITestCase
from apps.common.status import RecordStatus
from apps.common.testing import create_active_user, grant, grant_crud
from apps.product.models import Product, ProductType

class ProductApiTests(APITestCase):
    def setUp(self):
        self.user = create_active_user(username="nora", email="nora@storelab.test")
        grant_crud(self.user, "/api/product-types/", "/api/product-types/1/")
        grant_crud(self.user, "/api/products/", "/api/products/1/")
        grant(self.user, "GET", "/api/products/available/")
        self.client.force_authenticate(user=self.user)
        self.product_type = ProductType.objects.create(name="Bebida", status=RecordStatus.ACTIVE)

    def test_product_type_crud(self):
        created = self.client.post(
            "/api/product-types/",
            {"name": "Lácteo", "description": "Fríos"},
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["status"], RecordStatus.INACTIVE)
        pk = created.data["id"]
        self.assertEqual(self.client.get("/api/product-types/").status_code, 200)
        detail = self.client.get(f"/api/product-types/{pk}/")
        self.assertEqual(detail.data["name"], "Lácteo")
        updated = self.client.patch(
            f"/api/product-types/{pk}/",
            {"status": "active"},
            format="json",
        )
        self.assertEqual(updated.status_code, 200)
        deleted = self.client.delete(f"/api/product-types/{pk}/")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(ProductType.objects.get(pk=pk).status, RecordStatus.INACTIVE)

    def test_product_retrieve_update_and_soft_delete(self):
        created = self.client.post(
            "/api/products/",
            {
                "productTypeId": self.product_type.id,
                "name": "Leche",
                "price": "3.20",
                "stock": 2,
                "status": "active",
            },
            format="json",
        )
        pk = created.data["id"]
        detail = self.client.get(f"/api/products/{pk}/")
        self.assertEqual(detail.status_code, 200)
        updated = self.client.patch(f"/api/products/{pk}/", {"stock": 9}, format="json")
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["stock"], 9)
        deleted = self.client.delete(f"/api/products/{pk}/")
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(Product.objects.get(pk=pk).status, RecordStatus.INACTIVE)

    def test_default_status_and_type_restriction(self):
        created = self.client.post(
            "/api/products/",
            {"productTypeId": self.product_type.id, "name": "Té", "price": "1.00"},
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["status"], "inactive")
        self.assertEqual(created.data["stock"], 0)
        with self.assertRaises(RestrictedError):
            self.product_type.delete()

    def test_duplicate_product_name(self):
        payload = {"productTypeId": self.product_type.id, "name": "Café", "price": "3.00"}
        self.assertEqual(self.client.post("/api/products/", payload, format="json").status_code, 201)
        self.assertEqual(self.client.post("/api/products/", payload, format="json").status_code, 400)
        self.assertEqual(Product.objects.get(name="Café").price, Decimal("3.00"))

    def test_product_crud_and_available_filter(self):
        created = self.client.post(
            "/api/products/",
            {
                "productTypeId": self.product_type.id,
                "name": "Agua",
                "price": "2.50",
                "stock": 4,
                "status": "active",
            },
            format="json",
        )
        self.assertEqual(created.status_code, 201)
        available = self.client.get("/api/products/available/")
        self.assertEqual(available.status_code, 200)
        self.assertEqual(len(available.data), 1)
        Product.objects.filter(pk=created.data["id"]).update(stock=0)
        empty = self.client.get("/api/products/available/")
        self.assertEqual(empty.data, [])
