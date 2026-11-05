from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError, RestrictedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Owner, Pet
from .serializers import OwnerSerializer, PetSerializer

class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

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

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])
