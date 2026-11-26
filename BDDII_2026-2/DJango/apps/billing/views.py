from rest_framework import viewsets
from apps.security.ownership import scope_to_authenticated_owner
from .models import Payment, PaymentAudit
from .serializers import PaymentSerializer, PaymentAuditSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return scope_to_authenticated_owner(
            super().get_queryset(),
            self.request.user,
            'appointment__pet__owner__email',
        )

class PaymentAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentAudit.objects.order_by('-changed_at', '-pk')
    serializer_class = PaymentAuditSerializer
