from rest_framework.routers import SimpleRouter

from .views import OwnerViewSet, PetViewSet

router = SimpleRouter(use_regex_path=False)
router.register("owners", OwnerViewSet, basename="owner")
router.register("pets", PetViewSet, basename="pet")

urlpatterns = router.urls