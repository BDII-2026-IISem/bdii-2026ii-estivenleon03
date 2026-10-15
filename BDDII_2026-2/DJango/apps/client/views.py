from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.common.status import RecordStatus
from apps.client.models import Client
from apps.client.serializers import ClientSerializer
from apps.security.permissions import HasResourceAccess

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, HasResourceAccess]
    lookup_value_converter = "int"

    def perform_destroy(self, instance):
        instance.status = RecordStatus.INACTIVE
        instance.save(update_fields=["status", "updated_at"])
