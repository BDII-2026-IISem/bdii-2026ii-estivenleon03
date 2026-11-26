def has_active_role(user, role_name):
    return bool(
        user
        and user.is_authenticated
        and user.huellavet_role_assignments.filter(
            is_active=True,
            role__is_active=True,
            role__name=role_name,
        ).exists()
    )


def is_owner_portal_user(user):
    if not user or not user.is_authenticated or user.is_staff or user.is_superuser:
        return False
    return has_active_role(user, "PROPIETARIO") and not has_active_role(user, "ADMIN")


def scope_to_authenticated_owner(queryset, user, owner_email_lookup):
    if not is_owner_portal_user(user):
        return queryset

    email = (user.email or "").strip()
    if not email:
        return queryset.none()
    return queryset.filter(**{f"{owner_email_lookup}__iexact": email})
