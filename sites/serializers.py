
from django.utils.translation import ugettext as _
from rest_framework import serializers, validators

from .models import Schema, SchemaSection, Tip, Inspiration, Story, StoryEvent, Wish, Like, \
                    Photo, Theme, ThemeOption, ThemeTuning, Music

from appstore.serializers import StoryAppSerializer
from search.serializers import UniversalTagSerializer


class ThemeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeOption
        fields = ('name', 'image', 'title', 'description')


class ThemeTuningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeTuning
        fields = ('section', 'category', 'name', 'title', 'image', 'is_default')


class ThemeSerializer(serializers.ModelSerializer):
    options = ThemeOptionSerializer(many=True, source='themeoption_set', read_only=True)
    tunings = ThemeTuningSerializer(many=True, source='themetuning_set', read_only=True)

    class Meta:
        model = Theme
        fields = ('name', 'image', 'title', 'description', 'urlroot', 'options', 'tunings', 'data')


class TipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tip
        fields = ('id', 'style', 'order', 'text')


class InspirationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspiration
        fields = ('id', 'style', 'text')


class SchemaSectionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='section.name', read_only=True)
    # tips = TipSerializer(source='tip_set', many=True, read_only=True)
    # inspirations = InspirationSerializer(source='inspiration_set', many=True, read_only=True)

    class Meta:
        model = SchemaSection
        fields = ('id', 'name', 'title', 'description', 'image', 'order', 'data')  # , 'tips', 'inspirations')
        read_only_fields = ('title', 'description', 'order', 'data')


class SchemaSerializer(serializers.ModelSerializer):
    sections = SchemaSectionSerializer(many=True, source='schemasection_set', read_only=True)

    class Meta:
        model = Schema
        fields = ('id', 'name', 'title', 'description', 'image', 'data', 'sections', 'is_generic')
        read_only_fields = ('name', 'title', 'description', 'data')


class StoryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryEvent
        fields = ('id', 'story', 'last_modified', 'name', 'title', 'description', 'archived', 'order', 'data')
        read_only_fields = ('story', 'archived')


class StoryEventCreateSerializer(StoryEventSerializer):
    order = serializers.IntegerField(required=False, default=9999)
    data = serializers.DictField(required=False, default={})
    title = serializers.CharField(required=False, default={})
    name = serializers.CharField()

    class Meta(StoryEventSerializer.Meta):
        read_only_fields = []

    def validate_story(self, value):
        story = value
        if not story.schema.is_generic:
            raise serializers.ValidationError(_("Storyevent creation is not supported in non-generic stories"))
        return value

    def validate(self, data):
        section_name = data.get('name')
        storyevent_queryset = Story.objects.get(name='prototype_generic') \
                                   .storyevent_set.filter(schemasection__section__name=section_name)
        if not storyevent_queryset.exists():
            raise serializers.ValidationError(_("Invalid section name"))
        storyevent = storyevent_queryset.first()
        data['schemasection'] = storyevent.schemasection
        data['title'] = storyevent.title
        data['data'] = storyevent.data
        return data


class StorySerializer(serializers.ModelSerializer):
    # name = serializers.CharField(max_length=20, min_length=6,
    #                              validators=[validators.UniqueValidator(queryset=Story.objects.all())])
    schema = SchemaSerializer(read_only=True)
    likes = serializers.IntegerField(source='statistics.likes', read_only=True)

    storyEvents = serializers.SerializerMethodField()
    storyApps = serializers.SerializerMethodField()
    storyTags = serializers.SerializerMethodField()

    def get_storyEvents(self, obj):
        storyEvents = obj.storyevent_set.filter(archived=False)
        serializer = StoryEventSerializer(storyEvents, many=True)
        return serializer.data

    def get_storyApps(self, obj):
        storyApps = obj.storyapp_set.filter(archived=False)
        serializer = StoryAppSerializer(storyApps, many=True)
        return serializer.data

    def get_storyTags(self, obj):
        storyTags = obj.tags.all()
        serializer = UniversalTagSerializer(storyTags, many=True)
        return serializer.data

    class Meta:
        model = Story
        fields = ('id', 'last_modified', 'time_created', 'name', 'title', 'description', 'legacy', 'archived',
                  'schema', 'theme', 'css', 'data', 'likes', 'vendor', 'storyEvents', 'storyApps', 'storyTags')
        read_only_fields = ('name', 'theme', 'vendor', 'archived', 'legacy', 'css')


class SimpleStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id', 'last_modified', 'time_created', 'name', 'title', 'description',
                  'legacy', 'archived', 'theme', 'data', 'vendor')
        read_only_fields = ('name', 'theme', 'vendor', 'archived', 'legacy')


class WishSerializer(serializers.ModelSerializer):
    reply_name = serializers.ReadOnlyField(source='reply_to.name')

    class Meta:
        model = Wish
        fields = ('id', 'reply_to', 'reply_name', 'user', 'story', 'avatar', 'name', 'message', 'time_created')


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'user', 'story', 'time_created')


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'title', 'description', 'url', 'path')


class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = ('id', 'title', 'url')
