
from django.conf.urls import patterns, url, include
from rest_framework import routers
from .apiviews import PlaceViewSet, GreetingViewSet

router = routers.DefaultRouter()
router.register(r'place', PlaceViewSet)
router.register(r'greeting', GreetingViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
