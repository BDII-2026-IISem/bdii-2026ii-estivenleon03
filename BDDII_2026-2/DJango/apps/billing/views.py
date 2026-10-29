from rest_framework import viewsets
from .models import Payment, PaymentAudit
from .serializers import PaymentSerializer, PaymentAuditSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PaymentAuditViewSet(viewsets.ModelViewSet):
    queryset = PaymentAudit.objects.all()
    serializer_class = PaymentAuditSerializer
