
from django.conf.urls import patterns, url, include
from rest_framework import routers
from .apiviews import PlaceViewSet

router = routers.DefaultRouter()
router.register(r'place', PlaceViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
