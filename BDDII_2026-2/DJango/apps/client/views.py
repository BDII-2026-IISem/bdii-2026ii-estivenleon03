from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from apps.security.ownership import has_active_role, is_owner_portal_user
from apps.patient.views import OwnerViewSet

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(OwnerViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def partial_update(self, request, *args, **kwargs):
        is_veterinarian = (
            has_active_role(request.user, "VETERINARIO")
            and not request.user.is_staff
            and not request.user.is_superuser
        )
        if is_owner_portal_user(request.user) or is_veterinarian:
            if not set(request.data).issubset({"phone", "address"}):
                raise PermissionDenied(
                    "Solo puede actualizar el teléfono y la dirección."
                )
            return viewsets.ModelViewSet.partial_update(
                self,
                request,
                *args,
                **kwargs,
            )
        return super().partial_update(request, *args, **kwargs)
