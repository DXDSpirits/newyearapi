
from django.conf.urls import url, include
from rest_framework import routers
from .apiviews import PlaceViewSet, GreetingViewSet, PfopNotifyView, \
    ProvinceListView, CityListView, DistrictListView

router = routers.DefaultRouter()
router.register(r'place/province', ProvinceListView, base_name='place_list_of_provinces')
router.register(r'place/city', CityListView, base_name='place_list_of_cities')
router.register(r'place/district', DistrictListView, base_name='place_list_of_districts')
router.register(r'place', PlaceViewSet)
router.register(r'greeting', GreetingViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^pfop-notify/$', PfopNotifyView.as_view(), name='greetings-pfop-notify'),
]
