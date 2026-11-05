from django.contrib.auth import get_user_model

from apps.security.models import Permission, Role, RolePermission, UserRole

PASSWORD = "StoreLab-Test-1"


def create_active_user(username="ana", email="ana@storelab.test", password=PASSWORD):
    return get_user_model().objects.create_user(
        username=username,
        email=email,
        password=password,
    )


def grant(user, method, path, role_name=None):
    role, _created = Role.objects.get_or_create(
        name=role_name or f"test-role-{user.pk}",
        defaults={"description": "Rol de prueba"},
    )
    UserRole.objects.get_or_create(
        role=role,
        auth_user=user,
        defaults={"is_active": True},
    )
    permission, _created = Permission.objects.get_or_create(
        http_method=method.upper(),
        resource=path,
        defaults={"description": f"{method.upper()} {path}"},
    )
    RolePermission.objects.get_or_create(
        permission=permission,
        role=role,
        defaults={"is_active": True},
    )
    return role


def grant_crud(user, collection, detail):
    grant(user, "GET", collection)
    grant(user, "POST", collection)
    for method in ("GET", "PUT", "PATCH", "DELETE"):
        grant(user, method, detail)
