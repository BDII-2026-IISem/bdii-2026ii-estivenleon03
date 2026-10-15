from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.common.status import RecordStatus
from apps.sale.models import Sale
from apps.sale.serializers import SaleRegisterSerializer, SaleSerializer
from apps.security.permissions import HasResourceAccess

class SaleReadViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, HasResourceAccess]
    serializer_class = SaleSerializer
    lookup_value_converter = "int"

    def get_queryset(self):
        return Sale.objects.select_related("client").prefetch_related("lines__product")

    def perform_destroy(self, instance):
        instance.void()

class SaleRegisterAPIView(APIView):
    permission_classes = [IsAuthenticated, HasResourceAccess]

    @extend_schema(
        request=SaleRegisterSerializer,
        responses={201: SaleSerializer},
    )
    def post(self, request):
        serializer = SaleRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()
        sale = Sale.objects.prefetch_related("lines__product").get(pk=sale.pk)
        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)

class SaleCollectionAPIView(APIView):
    permission_classes = [IsAuthenticated, HasResourceAccess]

    @extend_schema(
        responses={200: SaleSerializer(many=True)},
        operation_id="sales_list",
    )
    def get(self, request, *args, **kwargs):
        return SaleReadViewSet.as_view({"get": "list"})(request._request, *args, **kwargs)

    @extend_schema(
        request=SaleRegisterSerializer,
        responses={201: SaleSerializer},
        operation_id="sales_create",
    )
    def post(self, request, *args, **kwargs):
        handler = SaleRegisterAPIView()
        handler.request = request
        handler.format_kwarg = None
        handler.args = ()
        handler.kwargs = {}
        return handler.post(request)
