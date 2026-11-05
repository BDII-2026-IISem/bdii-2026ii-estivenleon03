from rest_framework import viewsets
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = Appointment.StatusChoices.CANCELLED
        instance.save(update_fields=['is_active', 'status', 'updated_at'])
