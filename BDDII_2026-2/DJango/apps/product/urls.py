from django.urls import path
from rest_framework.routers import SimpleRouter
from apps.product.views import AvailableProductListAPIView, ProductTypeViewSet, ProductViewSet

router = SimpleRouter(use_regex_path=False)
router.register("product-types", ProductTypeViewSet, basename="product-type")
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path(
        "products/available/",
        AvailableProductListAPIView.as_view(),
        name="product-available",
    ),
]
urlpatterns += router.urls
