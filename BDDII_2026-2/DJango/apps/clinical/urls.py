from rest_framework.routers import SimpleRouter

from .views import (
    ConsultationViewSet,
    PrescriptionViewSet,
    VaccineApplicationViewSet,
    VaccineBatchViewSet,
    VaccineViewSet,
)

router = SimpleRouter(use_regex_path=False)
router.register("consultations", ConsultationViewSet, basename="consultation")
router.register("prescriptions", PrescriptionViewSet, basename="prescription")
router.register("vaccines", VaccineViewSet, basename="vaccine")
router.register("vaccine-batches", VaccineBatchViewSet, basename="vaccinebatch")
router.register(
    "vaccine-applications",
    VaccineApplicationViewSet,
    basename="vaccineapplication",
)

urlpatterns = router.urls