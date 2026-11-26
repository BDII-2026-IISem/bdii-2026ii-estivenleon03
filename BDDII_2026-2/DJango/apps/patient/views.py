from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError, RestrictedError
from rest_framework.exceptions import PermissionDenied
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.security.ownership import (
    has_active_role,
    is_owner_portal_user,
    scope_to_authenticated_owner,
)
from .models import Owner, Pet
from .serializers import OwnerSerializer, PetSerializer

class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

    def get_queryset(self):
        return scope_to_authenticated_owner(
            super().get_queryset(),
            self.request.user,
            "email",
        )

    def partial_update(self, request, *args, **kwargs):
        is_veterinarian = (
            has_active_role(request.user, "VETERINARIO")
            and not has_active_role(request.user, "ADMIN")
            and not request.user.is_staff
            and not request.user.is_superuser
        )
        if is_owner_portal_user(request.user) or is_veterinarian:
            if not set(request.data).issubset({"telefono", "direccion"}):
                raise PermissionDenied(
                    "Solo puede actualizar el teléfono y la dirección."
                )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['delete'], url_path='permanent-delete')
    @transaction.atomic
    def permanent_delete(self, request, pk=None):
        current = self.get_object()
        instance = Owner.objects.select_for_update().get(pk=current.pk)
        if instance.is_active:
            return Response(
                {'detail': 'Da de baja al propietario antes de solicitar su eliminación permanente.'},
                status=status.HTTP_409_CONFLICT,
            )
        if instance.pets.exists():
            return Response(
                {'detail': 'No se puede eliminar permanentemente un propietario que tiene mascotas asociadas. Puedes mantenerlo inactivo para conservar su historial.'},
                status=status.HTTP_409_CONFLICT,
            )
        if instance.sales.exists():
            return Response(
                {'detail': 'No se puede eliminar permanentemente un propietario con ventas asociadas. Mantén el registro inactivo para conservar el historial.'},
                status=status.HTTP_409_CONFLICT,
            )
        try:
            with transaction.atomic():
                instance.delete()
        except (IntegrityError, ProtectedError, RestrictedError):
            return Response(
                {
                    'detail': (
                        'No se puede eliminar permanentemente el propietario '
                        'porque existen registros relacionados. Conserva el '
                        'registro inactivo para mantener el historial.'
                    ),
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    def get_queryset(self):
        return scope_to_authenticated_owner(
            super().get_queryset(),
            self.request.user,
            "owner__email",
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])
