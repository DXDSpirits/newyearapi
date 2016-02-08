
from rest_framework import serializers

from users.serializers import UserProfileSerializer
from .models import Place, Greeting, Inspiration, Like, Share, Relay


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'category', 'parent', 'name']


class PlaceGreetingSerializer(serializers.ModelSerializer):
    greetings = serializers.SerializerMethodField()
    boundary = serializers.SerializerMethodField()

    def get_greetings(self, obj):
        greetings = obj.greetings.filter(status='online')
        return greetings.count()

    def get_boundary(self, obj):
        return []
        # boundary = (obj.data or {}).get('boundary', [])
        # return boundary

    class Meta:
        model = Place
        fields = ['id', 'name', 'greetings', 'boundary']


class GreetingSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    places = PlaceSerializer(many=True, read_only=True)
    place_id = serializers.IntegerField(write_only=True)
    key = serializers.CharField(write_only=True)

    def create(self, validated_data):
        place_id = validated_data.pop('place_id')
        greeting = super(GreetingSerializer, self).create(validated_data)
        place = Place.objects.filter(id=place_id).first()
        places = []
        while place is not None:
            places.append(place)
            place = place.parent
        greeting.places.add(*places)
        return greeting

    class Meta:
        model = Greeting
        fields = ['id', 'owner_id', 'time_created', 'url', 'status', 'title', 'description',
                  'profile', 'places', 'place_id', 'key']
        read_only_fields = ['owner_id', 'status']


class InspirationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspiration
        fields = ['id', 'text']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'owner_id', 'greeting', 'time_created']


class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['id', 'owner_id', 'time_created']
        read_only_fields = ['owner_id']


class RelaySerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = Relay
        fields = ['id', 'owner_id', 'profile', 'parent_id', 'time_created']
        read_only_fields = ['owner_id']
