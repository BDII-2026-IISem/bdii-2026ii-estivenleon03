from rest_framework import mixins, viewsets
from apps.security.ownership import scope_to_authenticated_owner
from .models import Consultation, Prescription, Vaccine, VaccineBatch, VaccineApplication
from .serializers import ConsultationSerializer, PrescriptionSerializer, VaccineSerializer, VaccineBatchSerializer, VaccineApplicationSerializer

class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer

    def get_queryset(self):
        return scope_to_authenticated_owner(
            super().get_queryset(),
            self.request.user,
            "pet__owner__email",
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def get_queryset(self):
        return scope_to_authenticated_owner(
            super().get_queryset(),
            self.request.user,
            "consultation__pet__owner__email",
        )

class VaccineViewSet(viewsets.ModelViewSet):
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer

class VaccineBatchViewSet(viewsets.ModelViewSet):
    queryset = VaccineBatch.objects.all()
    serializer_class = VaccineBatchSerializer

class VaccineApplicationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = VaccineApplication.objects.all()
    serializer_class = VaccineApplicationSerializer

    def get_queryset(self):
        return scope_to_authenticated_owner(
            super().get_queryset(),
            self.request.user,
            "consultation__pet__owner__email",
        )
