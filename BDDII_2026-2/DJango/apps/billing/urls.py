from rest_framework.routers import SimpleRouter

from .views import PaymentAuditViewSet, PaymentViewSet

router = SimpleRouter(use_regex_path=False)
router.register("payments", PaymentViewSet, basename="payment")
router.register("payment-audits", PaymentAuditViewSet, basename="paymentaudit")

urlpatterns = router.urls