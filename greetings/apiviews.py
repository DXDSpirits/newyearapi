
from rest_framework import viewsets, pagination

from .models import Place, Greeting
from .serializers import PlaceSerializer, GreetingSerializer
from .permissions import IsOwnerOrReadOnly

import django_filters


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class GreetingFilter(django_filters.FilterSet):
    place = django_filters.CharFilter(name='places__id')

    class Meta:
        model = Greeting
        fields = ['place']
        order_by = ['-id']


class GreetingPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class GreetingViewSet(viewsets.ModelViewSet):
    queryset = Greeting.objects.all()
    serializer_class = GreetingSerializer
    filter_class = GreetingFilter
    pagination_class = GreetingPagination
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)
