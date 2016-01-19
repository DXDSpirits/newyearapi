
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework import views, viewsets, pagination, response, status, decorators, renderers
from rest_framework_extensions.mixins import ReadOnlyCacheResponseAndETAGMixin

from .models import Place, Greeting
from .serializers import PlaceSerializer, PlaceGreetingSerializer, GreetingSerializer
from .permissions import IsOwnerOrReadOnly

import django_filters


class PfopNotifyView(views.APIView):
    def post(self, request):
        inputKey = request.data['inputKey']
        greeting = Greeting.objects.filter(key=inputKey).first()
        if greeting is not None and greeting.status == 'raw':
            newkey = request.data['items'][0]['key']
            greeting.data = request.data
            greeting.url = greeting.url.replace(greeting.key, newkey)
            greeting.key = ''
            greeting.status = 'online'
            greeting.save()
        return response.Response(status.HTTP_204_NO_CONTENT)


class PlaceViewSet(ReadOnlyCacheResponseAndETAGMixin,
                   viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    @decorators.list_route(methods=['get'])
    def province(self, request):
        queryset = Place.objects.filter(category='province')
        serializer = PlaceGreetingSerializer(queryset, many=True)
        return response.Response(serializer.data)

    @decorators.list_route(methods=['get'])
    def city(self, request):
        province = request.query_params.get('province')
        if province is not None and province.isdigit():
            queryset = Place.objects.filter(category='city', parent_id=province)
            serializer = PlaceGreetingSerializer(queryset, many=True)
            return response.Response(serializer.data)
        else:
            return response.Response(status.HTTP_204_NO_CONTENT)

    @decorators.detail_route(methods=['put'])
    def boundary(self, request, pk=None):
        place = self.get_object()
        if place.data is None:
            place.data = {}
        place.data['boundary'] = request.data.get('boundary', [])
        place.save(update_fields=['data'])
        serializer = PlaceGreetingSerializer(place)
        return response.Response(serializer.data)


class GreetingFilter(django_filters.FilterSet):
    place = django_filters.CharFilter(name='places__id')
    owner = django_filters.NumberFilter(name='owner_id')

    class Meta:
        model = Greeting
        fields = ['place', 'owner']
        order_by = ['-id']


class GreetingPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class GreetingViewSet(viewsets.ModelViewSet):
    queryset = Greeting.objects.filter(status='online').order_by('-id')
    serializer_class = GreetingSerializer
    filter_class = GreetingFilter
    pagination_class = GreetingPagination
    permission_classes = [IsOwnerOrReadOnly]

    @decorators.list_route(methods=['get'], renderer_classes=[renderers.TemplateHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        paginator = Paginator(self.get_queryset(), 20)
        page = request.GET.get('page')
        try:
            greetings = paginator.page(page)
        except PageNotAnInteger:
            greetings = paginator.page(1)
        except EmptyPage:
            greetings = paginator.page(paginator.num_pages)

        return response.Response({
            'greetings': greetings
        }, template_name='greetings.html')

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id, status='raw')
