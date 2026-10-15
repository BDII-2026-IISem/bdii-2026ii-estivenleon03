from rest_framework.routers import SimpleRouter
from apps.client.views import ClientViewSet

router = SimpleRouter(use_regex_path=False)
router.register("clients", ClientViewSet, basename="client")

urlpatterns = router.urls
