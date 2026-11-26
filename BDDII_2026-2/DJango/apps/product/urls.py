from rest_framework.routers import SimpleRouter

from .views import ProductTypeViewSet, ProductViewSet

router = SimpleRouter(use_regex_path=False)
router.register("product-types", ProductTypeViewSet, basename="producttype")
router.register("products", ProductViewSet, basename="product")

urlpatterns = router.urls