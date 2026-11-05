from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.urls import resolve
from apps.security.models import Permission, Role, RolePermission, User, UserRole

class Command(BaseCommand):
    help = "Sincroniza las rutas del sistema en la matriz RBAC y concede permisos al rol admin."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Asigna el rol admin a un usuario existente.",
        )

    def handle(self, *args, **options):
        collections = (
            "users", "roles", "permissions", "user-roles", "role-permissions",
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
            ("GET", "/api/v1/products/available/"),
            ("POST", "/api/v1/sales/1/payments/"),
            ("GET", "/api/v1/payment-audits/"),
            ("GET", "/api/v1/payment-audits/1/"),
        ])

        with transaction.atomic():
            admin_role, _ = Role.objects.get_or_create(
                name="ADMIN",
                defaults={"description": "Rol Administrador del Sistema"},
            )
            count = 0
            for method, path in sample_endpoints:
                resolve(path)
                segments = path.strip('/').split('/')
                route_pattern = '/' + '/'.join(
                    ':id' if segment == '1' else segment
                    for segment in segments
                )
                permission, _ = Permission.objects.get_or_create(
                    http_method=method,
                    resource=route_pattern,
                    defaults={"description": f"{method} {route_pattern}"},
                )
                RolePermission.objects.get_or_create(
                    permission=permission,
                    role=admin_role,
                )
                count += 1

            RolePermission.objects.filter(
                role=admin_role,
                permission__resource__in=(
                    "/api/v1/payment-audits",
                    "/api/v1/payment-audits/:id",
                ),
            ).exclude(permission__http_method="GET").delete()

            username = options.get("username")
            if username:
                auth_user = get_user_model().objects.filter(username=username).first()
                if auth_user is None:
                    raise CommandError(f"Usuario Django {username} no encontrado.")
                legacy_user = User.objects.filter(auth_user=auth_user, is_active=True).first()
                UserRole.objects.get_or_create(
                    auth_user=auth_user,
                    role=admin_role,
                    defaults={"user": legacy_user, "is_active": True},
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Rol ADMIN asignado al usuario {username}."
                ))

        self.stdout.write(self.style.SUCCESS(
            f"Permisos RBAC sincronizados. Total procesados: {count}."
        ))
