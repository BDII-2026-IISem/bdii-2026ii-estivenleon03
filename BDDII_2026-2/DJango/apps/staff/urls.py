from rest_framework.routers import SimpleRouter

from .views import VeterinarianViewSet

router = SimpleRouter(use_regex_path=False)
router.register("veterinarians", VeterinarianViewSet, basename="veterinarian")

urlpatterns = router.urls