from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Owner, Pet
from .serializers import OwnerSerializer, PetSerializer

class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

    @action(detail=True, methods=['delete'], url_path='permanent-delete')
    def permanent_delete(self, request, pk=None):
        instance = self.get_object()
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
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
