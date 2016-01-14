
from rest_framework import viewsets

from .models import Place
from .serializers import PlaceSerializer
from .permissions import IsOwner


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = (IsOwner,)
