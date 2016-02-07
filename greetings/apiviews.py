from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.utils.six.moves.urllib import parse as urlparse

from rest_framework import views, viewsets, pagination, response, status, decorators, \
    renderers, mixins, throttling, permissions
from rest_framework.generics import get_object_or_404

from rest_framework_extensions.mixins import ReadOnlyCacheResponseAndETAGMixin, DetailSerializerMixin

from qiniu import Auth, PersistentFop, op_save

from .models import Place, Greeting, Like, Inspiration, Share
from .models import get_relay_ranking, get_relays
from .serializers import PlaceSerializer, PlaceGreetingSerializer, GreetingSerializer, \
    LikeSerializer, InspirationSerializer, ShareSerializer, RelaySerializer
from .permissions import IsOwnerOrReadOnly

import django_filters

import logging
logger = logging.getLogger('apps')


class PfopNotifyView(views.APIView):
    def post(self, request):
        inputKey = request.data['inputKey']
        greeting = Greeting.objects.filter(key=inputKey).first()
        if greeting is not None and greeting.status == 'raw':
            try:
                newkey = request.data['items'][0]['key']
                greeting.data = request.data
                greeting.url = greeting.url.replace(greeting.key, newkey)
                greeting.key = ''
                greeting.status = 'online'
                greeting.save()
            except Exception as e:
                greeting.data = request.data
                greeting.save()
                logger.error('Pfop Notify Error. %s.' % e, extra={'request': self.request})
                return response.Response(status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response(status.HTTP_204_NO_CONTENT)


class PlaceViewSet(ReadOnlyCacheResponseAndETAGMixin,
                   viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer

    @decorators.detail_route(methods=['put'])
    def boundary(self, request, pk=None):
        place = self.get_object()
        if place.data is None:
            place.data = {}
        place.data['boundary'] = request.data.get('boundary', [])
        place.save(update_fields=['data'])
        serializer = PlaceGreetingSerializer(place)
        return response.Response(serializer.data)


class ProvinceListView(ReadOnlyCacheResponseAndETAGMixin,
                       viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.filter(category='province')
    serializer_class = PlaceGreetingSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        if isinstance(serializer.data, list):
            data = sorted(data, key=lambda item: -item.get('greetings', 0))
        return response.Response(data)


class CityListView(ReadOnlyCacheResponseAndETAGMixin,
                   viewsets.ReadOnlyModelViewSet):
    class PlaceFilter(django_filters.FilterSet):
        class Meta:
            model = Place
            fields = ['province']
        province = django_filters.NumberFilter(name='parent', required=True)
    queryset = Place.objects.filter(category='city')
    serializer_class = PlaceGreetingSerializer
    filter_class = PlaceFilter


class DistrictListView(ReadOnlyCacheResponseAndETAGMixin,
                       viewsets.ReadOnlyModelViewSet):
    class PlaceFilter(django_filters.FilterSet):
        class Meta:
            model = Place
            fields = ['city']
        city = django_filters.NumberFilter(name='parent', required=True)
    queryset = Place.objects.filter(category='district')
    serializer_class = PlaceGreetingSerializer
    filter_class = PlaceFilter


class GreetingFilter(django_filters.FilterSet):
    place = django_filters.NumberFilter(name='places__id')
    owner = django_filters.NumberFilter(name='owner_id')

    class Meta:
        model = Greeting
        fields = ['place', 'owner']
        order_by = ['-id']


class GreetingPagination(pagination.PageNumberPagination):
    page_size = 9
    page_size_query_param = 'limit'


class GreetingViewSet(DetailSerializerMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Greeting.objects.filter(status='online').order_by('-id')
    queryset_detail = Greeting.objects.exclude(status='raw').order_by('-id')
    serializer_class = GreetingSerializer
    serializer_detail_class = GreetingSerializer
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

    def perform_pfop(self, instance):
        access_key = settings.QINIU['ACCESS_KEY']
        secret_key = settings.QINIU['SECRET_KEY']
        origin = self.request.build_absolute_uri('/')
        path = reverse('greetings-pfop-notify')
        notify_url = urlparse.urljoin(origin, path)

        auth = Auth(access_key, secret_key)
        pfop = PersistentFop(auth, 'tatmusic', 'wechataudio', notify_url)
        op = op_save('avthumb/mp3/aq/0', 'tatmusic', instance.key + '.mp3')
        ret, info = pfop.execute(instance.key, [op])
        if instance.data is None:
            instance.data = ret
        else:
            instance.data.update(ret)
        instance.save(update_fields=['data'])

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id, status='raw')
        self.perform_pfop(serializer.instance)


class UserGreetingView(views.APIView):
    def get(self, request, pk=None):
        greeting = get_object_or_404(Greeting.objects, owner_id=pk, status='online')
        serializer = GreetingSerializer(greeting)
        return response.Response(serializer.data)


class LikeViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):

    class LikeThrottling(throttling.UserRateThrottle):
        rate = '10/min'

    queryset = Like.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    throttle_classes = (LikeThrottling,)
    serializer_class = LikeSerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user
        greeting = request.query_params.get('greeting')
        if greeting is not None and greeting.isdigit():
            queryset = Like.objects.filter(greeting_id=greeting).order_by('-id')
        elif user.is_authenticated():
            user = self.request.user
            queryset = user.like_set.all().order_by('-id')
        else:
            queryset = Like.objects.none()
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request.data['owner_id'] = self.request.user.id
        return super(LikeViewSet, self).create(request, *args, **kwargs)


class InspirationViewSet(ReadOnlyCacheResponseAndETAGMixin,
                         viewsets.ReadOnlyModelViewSet):
    class Pagination(pagination.PageNumberPagination):
        page_size = 3

    class Filter(django_filters.FilterSet):
        place = django_filters.NumberFilter(name='places__id')

        class Meta:
            model = Inspiration
            fields = ['place']

    queryset = Inspiration.objects.annotate(num_places=Count('places')).order_by('num_places')
    serializer_class = InspirationSerializer
    filter_class = Filter
    pagination_class = Pagination


class ShareViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    class Pagination(pagination.PageNumberPagination):
        page_size = 1

    queryset = Share.objects.order_by('-id')
    serializer_class = ShareSerializer
    pagination_class = Pagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)


class RelayViewSet(mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    queryset = Share.objects.all()
    serializer_class = RelaySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)


class RankingView(views.APIView):
    def get(self, request, pk=None):
        if pk is None:
            data = get_relay_ranking()
        else:
            data = get_relays(int(pk))
        return response.Response(data)
