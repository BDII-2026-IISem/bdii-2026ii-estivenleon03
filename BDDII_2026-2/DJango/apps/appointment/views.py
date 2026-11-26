from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from apps.security.ownership import (
    is_owner_portal_user,
    scope_to_authenticated_owner,
)
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return scope_to_authenticated_owner(
            super().get_queryset(),
            self.request.user,
            "pet__owner__email",
        )

    def perform_create(self, serializer):
        pet = serializer.validated_data["pet"]
        if is_owner_portal_user(self.request.user):
            user_email = (self.request.user.email or "").strip().casefold()
            pet_owner_email = (pet.owner.email or "").strip().casefold()
            if not user_email or pet_owner_email != user_email:
                raise PermissionDenied(
                    "Solo puede solicitar citas para sus propias mascotas."
                )
        serializer.save()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = Appointment.StatusChoices.CANCELLED
        instance.save(update_fields=['is_active', 'status', 'updated_at'])
