from rest_framework import viewsets
from .models import Veterinarian
from .serializers import VeterinarianSerializer

class VeterinarianViewSet(viewsets.ModelViewSet):
    queryset = Veterinarian.objects.all()
    serializer_class = VeterinarianSerializer
