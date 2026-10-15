from django.core.management.base import BaseCommand
from django.urls import resolve
from apps.common.status import RecordStatus
from apps.security.models import Resource, ResourceRole, Role, RoleUser, User

class Command(BaseCommand):
    help = "Sincroniza las rutas del sistema en la matriz RBAC y concede permisos al rol admin."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Asigna el rol admin a un usuario existente.",
        )

    def handle(self, *args, **options):
        sample_endpoints = [
            # Clients
            ("GET", "/api/clients/"),
            ("POST", "/api/clients/"),
            ("GET", "/api/clients/1/"),
            ("PUT", "/api/clients/1/"),
            ("PATCH", "/api/clients/1/"),
            ("DELETE", "/api/clients/1/"),
            # Product Types
            ("GET", "/api/product-types/"),
            ("POST", "/api/product-types/"),
            ("GET", "/api/product-types/1/"),
            ("PUT", "/api/product-types/1/"),
            ("PATCH", "/api/product-types/1/"),
            ("DELETE", "/api/product-types/1/"),
            # Products
            ("GET", "/api/products/"),
            ("POST", "/api/products/"),
            ("GET", "/api/products/1/"),
            ("PUT", "/api/products/1/"),
            ("PATCH", "/api/products/1/"),
            ("DELETE", "/api/products/1/"),
            ("GET", "/api/products/available/"),
            # Sales
            ("GET", "/api/sales/"),
            ("POST", "/api/sales/"),
            ("GET", "/api/sales/1/"),
            ("DELETE", "/api/sales/1/"),
            # Users
            ("GET", "/api/users/"),
            ("POST", "/api/users/"),
            ("GET", "/api/users/1/"),
            ("PUT", "/api/users/1/"),
            ("PATCH", "/api/users/1/"),
            ("DELETE", "/api/users/1/"),
            # Roles
            ("GET", "/api/roles/"),
            ("POST", "/api/roles/"),
            ("GET", "/api/roles/1/"),
            ("PUT", "/api/roles/1/"),
            ("PATCH", "/api/roles/1/"),
            ("DELETE", "/api/roles/1/"),
            # RoleUsers
            ("GET", "/api/role-users/"),
            ("POST", "/api/role-users/"),
            ("GET", "/api/role-users/1/"),
            ("PUT", "/api/role-users/1/"),
            ("PATCH", "/api/role-users/1/"),
            ("DELETE", "/api/role-users/1/"),
            # Resources
            ("GET", "/api/resources/"),
            ("POST", "/api/resources/"),
            ("GET", "/api/resources/1/"),
            ("PUT", "/api/resources/1/"),
            ("PATCH", "/api/resources/1/"),
            ("DELETE", "/api/resources/1/"),
            # ResourceRoles
            ("GET", "/api/resource-roles/"),
            ("POST", "/api/resource-roles/"),
            ("GET", "/api/resource-roles/1/"),
            ("PUT", "/api/resource-roles/1/"),
            ("PATCH", "/api/resource-roles/1/"),
            ("DELETE", "/api/resource-roles/1/"),
        ]

        admin_role, _ = Role.objects.get_or_create(
            name="admin",
            defaults={"description": "Rol Administrador del Sistema", "status": RecordStatus.ACTIVE},
        )
        if admin_role.status != RecordStatus.ACTIVE:
            admin_role.status = RecordStatus.ACTIVE
            admin_role.save(update_fields=["status", "updated_at"])

        count = 0
        for method, path in sample_endpoints:
            match = resolve(path)
            route_pattern = match.route
            resource, _ = Resource.objects.get_or_create(
                method=method,
                route=route_pattern,
                defaults={
                    "name": f"{method} {route_pattern}",
                    "status": RecordStatus.ACTIVE,
                },
            )
            if resource.status != RecordStatus.ACTIVE:
                resource.status = RecordStatus.ACTIVE
                resource.save(update_fields=["status", "updated_at"])

            rr, _ = ResourceRole.objects.get_or_create(
                resource=resource,
                role=admin_role,
                defaults={"status": RecordStatus.ACTIVE},
            )
            if rr.status != RecordStatus.ACTIVE:
                rr.status = RecordStatus.ACTIVE
                rr.save(update_fields=["status", "updated_at"])
            count += 1

        username = options.get("username")
        if username:
            try:
                user = User.objects.get(username=username)
                ru, _ = RoleUser.objects.get_or_create(
                    role=admin_role,
                    user=user,
                    defaults={"status": RecordStatus.ACTIVE},
                )
                if ru.status != RecordStatus.ACTIVE:
                    ru.status = RecordStatus.ACTIVE
                    ru.save(update_fields=["status", "updated_at"])
                self.stdout.write(self.style.SUCCESS(f"Rol admin asignado al usuario {username}."))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Usuario {username} no encontrado."))

        self.stdout.write(self.style.SUCCESS(f"Recursos RBAC sincronizados. Total procesados: {count}."))
