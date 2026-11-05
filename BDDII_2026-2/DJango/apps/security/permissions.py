import re

from rest_framework.permissions import BasePermission

from apps.security.models import RolePermission


def _normalize_path(path):
    segments = [segment for segment in str(path).strip().split("/") if segment]
    if segments and segments[0] == "api":
        segments.pop(0)
        if segments and re.fullmatch(r"v\d+", segments[0]):
            segments.pop(0)
    return "/".join(segments)


def _path_matches(granted_path, candidates):
    normalized = _normalize_path(granted_path)
    expression = re.escape(normalized)
    expression = re.sub(r"<[^>]+>", r"[^/]+", expression)
    expression = re.sub(r"\\\{[^}]+\\\}", r"[^/]+", expression)
    expression = re.sub(r":[A-Za-z_][A-Za-z0-9_]*", r"[^/]+", expression)
    return any(re.fullmatch(expression, _normalize_path(path)) for path in candidates)


class HasResourceAccess(BasePermission):
    message = "No tiene autorización para ejecutar esta operación."

    def has_permission(self, request, view):
        if request.method.upper() == "OPTIONS":
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True

        match = request.resolver_match
        if match is None:
            return False

        method = request.method.upper()
        if method == "HEAD":
            method = "GET"

        candidates = [request.path_info]
        if match.route:
            candidates.append(match.route)

        return any(
            _path_matches(resource_path, candidates)
            for resource_path in RolePermission.objects.filter(
                is_active=True,
                role__is_active=True,
                permission__is_active=True,
                permission__http_method=method,
                role__user_assignments__auth_user=user,
                role__user_assignments__is_active=True,
            ).values_list("permission__resource", flat=True)
        )
