from rest_framework.routers import SimpleRouter

from .views import AppointmentViewSet

router = SimpleRouter(use_regex_path=False)
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = router.urls