from rest_framework import mixins, viewsets
from .models import Consultation, Prescription, Vaccine, VaccineBatch, VaccineApplication
from .serializers import ConsultationSerializer, PrescriptionSerializer, VaccineSerializer, VaccineBatchSerializer, VaccineApplicationSerializer

class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

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
