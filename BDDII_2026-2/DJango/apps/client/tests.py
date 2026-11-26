from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.client.models import Client
from apps.patient.models import Owner


@override_settings(API_ACCESS="open")
class ClientCompatibilityApiTests(APITestCase):
    def test_clients_route_uses_owner_table_and_starts_inactive(self):
        user = get_user_model().objects.create_user(
            username="client-api-user",
            password="test-password",
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            "/api/v1/clients/",
            {
                "name": "Ana Leon",
                "docType": "CC",
                "docNumber": "123456789",
                "email": "ana@example.test",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "inactive")
        self.assertIn("createdAt", response.data)
        self.assertNotIn("created_at", response.data)
        self.assertNotIn("password", response.data)
        owner = Owner.objects.get(doc_number="123456789")
        self.assertFalse(owner.is_active)
        self.assertTrue(Client.objects.filter(pk=owner.pk).exists())
        self.assertEqual(Client._meta.db_table, Owner._meta.db_table)
        self.assertTrue(Client._meta.proxy)

    def test_client_rejects_duplicate_email_case_insensitively(self):
        user = get_user_model().objects.create_user(
            username="client-email-user",
            password="test-password",
        )
        self.client.force_authenticate(user=user)
        Owner.objects.create(
            name="Ana Leon",
            doc_type="CC",
            doc_number="existing-client",
            email="ana@example.test",
        )

        response = self.client.post(
            "/api/v1/clients/",
            {
                "name": "Otra Ana",
                "docType": "CC",
                "docNumber": "new-client",
                "email": "ANA@example.test",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_owner_model_normalizes_email_and_hashes_client_password(self):
        owner = Owner(
            name="Ana Leon",
            doc_type="CC",
            doc_number="password-client",
            email=" ANA@EXAMPLE.TEST ",
        )
        owner.set_password("client-secret")
        owner.save()

        self.assertEqual(owner.email, "ana@example.test")
        self.assertNotEqual(owner.password, "client-secret")
        self.assertTrue(owner.check_password("client-secret"))
        self.assertFalse(owner.check_password("wrong-secret"))

    def test_owner_model_rejects_one_character_names(self):
        owner = Owner(
            name="A",
            doc_type="CC",
            doc_number="short-name-client",
        )

        with self.assertRaises(ValidationError) as context:
            owner.full_clean()

        self.assertIn("name", context.exception.message_dict)

    def test_owner_email_constraint_rejects_case_insensitive_duplicates(self):
        Owner.objects.create(
            name="Ana Leon",
            doc_type="CC",
            doc_number="first-email-owner",
            email="ana@example.test",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Owner.objects.create(
                    name="Otra Ana",
                    doc_type="CC",
                    doc_number="second-email-owner",
                    email="ANA@example.test",
                )
