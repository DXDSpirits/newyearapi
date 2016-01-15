
from rest_framework import serializers

from users.serializers import UserProfileSerializer
from .models import Place, Greeting


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'category', 'parent', 'name']


class PlaceGreetingSerializer(serializers.ModelSerializer):
    greetings = serializers.SerializerMethodField()

    def get_greetings(self, obj):
        greetings = obj.greetings.all()
        return greetings.count()

    class Meta:
        model = Place
        fields = ['id', 'name', 'greetings']


class GreetingSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    places = PlaceSerializer(many=True, read_only=True)
    place_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        place_id = validated_data.pop('place_id')
        place = Place.objects.filter(id=place_id).first()
        places = []
        while place is not None:
            places.append(place)
            place = place.parent
        greeting = super(GreetingSerializer, self).create(validated_data)
        greeting.places.add(*places)
        return greeting

    class Meta:
        model = Greeting
        fields = ['id', 'owner_id', 'time_created', 'url', 'profile', 'places', 'key', 'place_id']
        read_only_fields = ['owner_id']
