from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.urls import resolve

from apps.security.models import (
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
    normalize_resource_path,
)

ROLE_COLLECTION_ACCESS = {
    "VETERINARIO": {
        "clients": {"GET", "POST", "PATCH"},
        "owners": {"GET", "POST", "PATCH"},
        "pets": {"GET", "POST", "PATCH"},
        "veterinarians": {"GET"},
        "consultations": {"GET", "POST", "PATCH"},
        "prescriptions": {"GET", "POST", "PATCH"},
        "product-types": {"GET"},
        "products": {"GET", "PATCH"},
        "vaccines": {"GET"},
        "vaccine-batches": {"GET"},
        "vaccine-applications": {"GET", "POST"},
        "sales": {"GET"},
    },
    "RECEPCIONISTA": {
        "clients": {"GET", "POST", "PATCH"},
        "owners": {"GET", "POST", "PATCH"},
        "pets": {"GET", "POST", "PATCH"},
        "veterinarians": {"GET"},
        "appointments": {"GET", "POST", "PUT", "PATCH", "DELETE"},
        "consultations": {"GET"},
        "prescriptions": {"GET"},
        "product-types": {"GET"},
        "products": {"GET"},
        "vaccine-applications": {"GET"},
        "sales": {"GET", "POST", "PATCH"},
        "payments": {"GET", "POST", "PATCH"},
    },
    "PROPIETARIO": {
        "clients": {"GET", "PATCH"},
        "owners": {"GET", "PATCH"},
        "pets": {"GET"},
        "veterinarians": {"GET"},
        "appointments": {"GET", "POST", "DELETE"},
        "consultations": {"GET"},
        "prescriptions": {"GET"},
        "product-types": {"GET"},
        "products": {"GET"},
        "vaccines": {"GET"},
        "vaccine-batches": {"GET"},
        "vaccine-applications": {"GET"},
        "sales": {"GET"},
        "payments": {"GET"},
    },
}

ROLE_EXTRA_ACCESS = {
    "VETERINARIO": {
        ("GET", "/api/v1/products/available"),
    },
    "RECEPCIONISTA": {
        ("POST", "/api/v1/sales/:id/payments"),
        ("GET", "/api/v1/products/available"),
    },
    "PROPIETARIO": {
        ("GET", "/api/v1/auth/profile"),
        ("PATCH", "/api/v1/auth/profile"),
        ("GET", "/api/v1/products/available"),
    },
}


class Command(BaseCommand):
    help = "Sincroniza rutas y permisos para los roles del sistema."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Asigna el rol admin a un usuario existente.",
        )

    def handle(self, *args, **options):
        collections = (
            "users", "roles", "permissions", "user-roles", "role-permissions",
            "role-users", "resources", "resource-roles", "clients",
            "owners", "pets", "veterinarians", "appointments", "consultations",
            "prescriptions", "vaccines", "vaccine-batches", "vaccine-applications",
            "product-types", "products", "sales", "payments",
        )
        sample_endpoints = []
        for collection in collections:
            endpoint = f"/api/v1/{collection}/"
            sample_endpoints.extend((method, endpoint) for method in ("GET", "POST"))
            sample_endpoints.extend(
                (method, f"{endpoint}1/")
                for method in ("GET", "PUT", "PATCH", "DELETE")
            )
        sample_endpoints.extend([
            ("GET", "/api/v1/auth/profile/"),
            ("PATCH", "/api/v1/auth/profile/"),
            ("GET", "/api/v1/products/available/"),
            ("POST", "/api/v1/sales/1/payments/"),
            ("GET", "/api/v1/payment-audits/"),
            ("GET", "/api/v1/payment-audits/1/"),
        ])

        with transaction.atomic():
            roles = {}
            for name, description in (
                ("ADMIN", "Rol Administrador del Sistema"),
                ("VETERINARIO", "Atención médica y manejo de pacientes"),
                ("RECEPCIONISTA", "Atención al cliente, agenda y cobros"),
                ("PROPIETARIO", "Acceso al portal de mascotas del propietario"),
            ):
                role, _ = Role.objects.get_or_create(
                    name=name,
                    defaults={"description": description},
                )
                if not role.is_active or not role.description:
                    role.is_active = True
                    if not role.description:
                        role.description = description
                    role.save(update_fields=["is_active", "description"])
                roles[name] = role

            permissions = {}
            for method, path in sample_endpoints:
                resolve(path)
                segments = path.strip("/").split("/")
                route_pattern = normalize_resource_path("/".join(
                    ":id" if segment == "1" else segment
                    for segment in segments
                ))
                permission, _ = Permission.objects.get_or_create(
                    http_method=method,
                    resource=route_pattern,
                    defaults={"description": f"{method} {route_pattern}"},
                )
                if not permission.is_active:
                    permission.is_active = True
                    permission.save(update_fields=["is_active"])
                permissions[(method, route_pattern)] = permission

            self._sync_role_permissions(
                roles["ADMIN"],
                {
                    key
                    for key in permissions
                    if not (
                        key[1] in {
                            "/api/v1/payment-audits",
                            "/api/v1/payment-audits/:id",
                        }
                        and key[0] != "GET"
                    )
                },
                permissions,
            )

            for role_name, collection_access in ROLE_COLLECTION_ACCESS.items():
                desired = {
                    (method, normalize_resource_path(resource))
                    for method, resource in ROLE_EXTRA_ACCESS.get(role_name, set())
                }
                for method, resource in permissions:
                    parts = resource.strip("/").split("/")
                    if len(parts) < 3 or parts[0:2] != ["api", "v1"]:
                        continue
                    collection = parts[2]
                    collection_root = normalize_resource_path(
                        f"api/v1/{collection}"
                    )
                    collection_detail = normalize_resource_path(
                        f"api/v1/{collection}/<int:pk>"
                    )
                    if (
                        collection in collection_access
                        and resource in (collection_root, collection_detail)
                        and method in collection_access[collection]
                    ):
                        desired.add((method, resource))
                self._sync_role_permissions(
                    roles[role_name],
                    desired,
                    permissions,
                )

            username = options.get("username")
            if username:
                auth_user = get_user_model().objects.filter(username=username).first()
                if auth_user is None:
                    raise CommandError(f"Usuario Django {username} no encontrado.")
                legacy_user = User.objects.filter(
                    auth_user=auth_user,
                    is_active=True,
                ).first()
                UserRole.objects.update_or_create(
                    auth_user=auth_user,
                    role=roles["ADMIN"],
                    defaults={"user": legacy_user, "is_active": True},
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Rol ADMIN asignado al usuario {username}."
                ))

        self.stdout.write(self.style.SUCCESS(
            f"Permisos RBAC sincronizados. Total procesados: {len(permissions)}."
        ))

    @staticmethod
    def _sync_role_permissions(role, desired, permissions):
        granted_permissions = []
        for key in desired:
            permission = permissions.get(key)
            if permission is None:
                raise CommandError(f"Permiso no registrado: {key[0]} {key[1]}")
            RolePermission.objects.update_or_create(
                permission=permission,
                role=role,
                defaults={"is_active": True},
            )
            granted_permissions.append(permission)
        RolePermission.objects.filter(role=role).exclude(
            permission__in=granted_permissions,
        ).delete()
