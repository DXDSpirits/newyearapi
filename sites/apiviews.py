
from django.shortcuts import get_object_or_404

from .models import Schema, Story, StoryEvent, Wish, Photo, Tip, Inspiration, Theme, Like, Music
from .permissions import IsOwner
from .serializers import SchemaSerializer, StorySerializer, StoryEventSerializer, StoryEventCreateSerializer, \
    WishSerializer, LikeSerializer, PhotoSerializer, TipSerializer, InspirationSerializer, ThemeSerializer, \
    SimpleStorySerializer, MusicSerializer

from appstore.serializers import StoryAppSerializer
from search.models import UniversalTag

from .upgrade_generic import upgrade_to_generic

from rest_framework import viewsets, decorators, response, filters, permissions, status, throttling, mixins, pagination

from rest_framework_extensions.mixins import ReadOnlyCacheResponseAndETAGMixin

import django_filters
import random


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        pk = view.kwargs.get(view.lookup_field, None)
        method = request.method
        if (method in {'GET'} and pk is None):
            return queryset.filter(owner=request.user)
        else:
            return queryset


class ThemeViewSet(ReadOnlyCacheResponseAndETAGMixin,
                   viewsets.ReadOnlyModelViewSet):
    class Filter(django_filters.FilterSet):
        class Meta:
            model = Theme
            fields = ['schema']
            order_by = ['schematheme__order']
        schema = django_filters.CharFilter(name='schemas__name')
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    filter_class = Filter
    lookup_field = 'name'


class TipViewSet(ReadOnlyCacheResponseAndETAGMixin,
                 viewsets.ReadOnlyModelViewSet):
    class Pagination(pagination.PageNumberPagination):
        page_size = 10

    class Filter(django_filters.FilterSet):
        class Meta:
            model = Tip
            fields = ['schemasection']
            order_by = ['order']

    queryset = Tip.objects.all()
    serializer_class = TipSerializer
    filter_class = Filter
    pagination_class = Pagination


class InspirationViewSet(ReadOnlyCacheResponseAndETAGMixin,
                         viewsets.ReadOnlyModelViewSet):
    class Pagination(pagination.PageNumberPagination):
        page_size = 10

    class Filter(django_filters.FilterSet):
        tag = django_filters.ModelMultipleChoiceFilter(name='tags', to_field_name='name',
                                                       queryset=UniversalTag.objects.all())

        class Meta:
            model = Inspiration
            fields = ['style', 'tag']

    queryset = Inspiration.objects.all()
    serializer_class = InspirationSerializer
    filter_class = Filter
    pagination_class = Pagination


class SchemaViewSet(ReadOnlyCacheResponseAndETAGMixin,
                    viewsets.ReadOnlyModelViewSet):
    queryset = Schema.objects.all()
    serializer_class = SchemaSerializer
    lookup_field = 'name'


class StoryNameViewSet(mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    # queryset = Story.objects.using('readonly').filter(archived=False) \
    queryset = Story.objects.using('readonly') \
                    .prefetch_related('schema__schemasection_set__section')
    serializer_class = StorySerializer
    lookup_field = 'name'

    @decorators.detail_route(methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def clone(self, request, name=None):
        story = self.get_object()
        start = int('0xA000000', 16)
        end = int('0xFFFFFFF', 16)
        while True:
            num = random.randint(start, end)
            new_name = hex(num)[2:].lower()
            if not Story.objects.filter(name=new_name).exists():
                break
        new_story = Story.objects.clone(story, new_name, request.user)
        serializer = StorySerializer(new_story, context={'request': request})
        return response.Response(serializer.data)

    @decorators.detail_route(methods=['get'])
    def schema(self, request, name=None):
        story = get_object_or_404(Story, name=name)
        schema = story.schema
        serializer = SchemaSerializer(schema)
        return response.Response(serializer.data)

    @decorators.detail_route(methods=['get'])
    def themes(self, request, name=None):
        story = get_object_or_404(Story, name=name)
        # if story.storyevent_set.filter(schemasection__section__name='weddinghero').exists():
        #     queryset = Theme.objects.filter(name__in=['vintage', 'eternity', 'cartooncloud', 'floral', 'moderate', 'rose'])
        # else:
        #     queryset = Theme.objects.filter(schemas__id=story.schema_id).order_by('schematheme__order')
        queryset = Theme.objects.filter(schemas__id=story.schema_id).order_by('schematheme__order')
        queryset = queryset.prefetch_related('themeoption_set')
        serializer = ThemeSerializer(queryset, many=True)
        return response.Response(serializer.data)


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.filter(archived=False)
    serializer_class = StorySerializer
    permission_classes = (IsOwner,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_serializer_class(self):
        pk = self.kwargs.get(self.lookup_field, None)
        method = self.request.method
        if method == 'GET' and pk is None:
            return SimpleStorySerializer
        else:
            return self.serializer_class

    @decorators.detail_route(methods=['put'])
    def theme(self, request, pk=None):
        theme = request.data.get('theme')
        if theme is not None:
            story = self.get_object()
            story.theme = theme
            story.save(update_fields=['theme'])
            serializer = StorySerializer(story, context={'request': request})
            return response.Response(serializer.data)
        else:
            return response.Response()

    @decorators.detail_route(methods=['put'])
    def upgrade(self, request, pk=None):
        story = self.get_object()
        upgrade_to_generic(story)
        serializer = StorySerializer(story, context={'request': request})
        return response.Response(serializer.data)

    @decorators.detail_route(methods=['get'], serializer_class=None)
    def verify_owner(self, request, pk=None):
        self.get_object()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.detail_route(methods=['get'], permission_classes=[], filter_backends=[])
    def wishes(self, request, pk=None):
        queryset = self.get_object().wish_set.filter(approved=True).order_by('-id')
        serializer = WishSerializer(queryset, many=True, context={'request': request})
        return response.Response(serializer.data)

    @decorators.detail_route(methods=['post'], serializer_class=StoryEventCreateSerializer)
    def add_storyevent(self, request, pk=None):
        data = request.data
        data.update({'story': pk})
        serializer = StoryEventCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.detail_route(methods=['post'])
    def add_app(self, request, pk=None):
        data = request.data
        data.update({'story': pk})
        serializer = StoryAppSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        instance.archived = True
        instance.save(update_fields=['archived'])


class StoryEventViewSet(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = StoryEvent.objects.all()
    serializer_class = StoryEventSerializer
    permission_classes = (IsOwner,)
    filter_backends = (IsOwnerFilterBackend,)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        instance.archived = True
        instance.order = 99999
        instance.save(update_fields=['archived', 'order'])


class PhotoViewSet(viewsets.ModelViewSet):
    class PhotoPagination(pagination.PageNumberPagination):
        page_size = 24

    queryset = Photo.objects.all().order_by('-id')
    serializer_class = PhotoSerializer
    permission_classes = (IsOwner,)
    filter_backends = (IsOwnerFilterBackend,)
    pagination_class = PhotoPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        instance.owner = None
        instance.save(update_fields=['owner'])


class MusicViewSet(viewsets.ModelViewSet):
    class MusicPagination(pagination.PageNumberPagination):
        page_size = 24

    queryset = Music.objects.all().order_by('-id')
    serializer_class = MusicSerializer
    permission_classes = (IsOwner,)
    filter_backends = (IsOwnerFilterBackend,)
    pagination_class = MusicPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        instance.owner = None
        instance.save(update_fields=['owner'])


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
        story = request.query_params.get('story')
        if story is not None and story.isdigit():
            queryset = Like.objects.filter(story_id=story).order_by('-id')
        elif user.is_authenticated():
            user = self.request.user
            queryset = user.like_set.all().order_by('-id')
        else:
            queryset = Like.objects.none()
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.id
        return super(LikeViewSet, self).create(request, *args, **kwargs)


class WishViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    class WishPagination(pagination.PageNumberPagination):
        page_size = 20

    class WishFilter(django_filters.FilterSet):
        class Meta:
            model = Wish
            fields = ['story']
            order_by = ['-id']
        # story = django_filters.NumberFilter(required=True)
    queryset = Wish.objects.filter(approved=True)
    serializer_class = WishSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_class = WishFilter
    pagination_class = WishPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.approved = False
        instance.save(update_fields=['approved'])
