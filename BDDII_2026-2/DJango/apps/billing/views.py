from rest_framework import viewsets
from .models import Payment, PaymentAudit
from .serializers import PaymentSerializer, PaymentAuditSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PaymentAuditViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentAudit.objects.order_by('-changed_at', '-pk')
    serializer_class = PaymentAuditSerializer
