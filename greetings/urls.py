
from django.conf.urls import url, include
from django.views.decorators.cache import cache_page
from rest_framework import routers
from .apiviews import PlaceViewSet, GreetingViewSet, PfopNotifyView, UserGreetingView, \
    ProvinceListView, CityListView, DistrictListView, InspirationViewSet, LikeViewSet, \
    ShareViewSet, RelayViewSet, RankingView

router = routers.DefaultRouter()
router.register(r'place/province', ProvinceListView, base_name='place_list_of_provinces')
router.register(r'place/city', CityListView, base_name='place_list_of_cities')
router.register(r'place/district', DistrictListView, base_name='place_list_of_districts')
router.register(r'place', PlaceViewSet)
router.register(r'greeting', GreetingViewSet)
router.register(r'inspiration', InspirationViewSet)
router.register(r'like', LikeViewSet)
router.register(r'share', ShareViewSet)
router.register(r'relay', RelayViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^pfop-notify/$', PfopNotifyView.as_view(), name='greetings-pfop-notify'),
    url(r'^usergreeting/(?P<pk>\d+)/$', UserGreetingView.as_view(), name='greeting-from-user'),
    url(r'^ranking/((?P<pk>\d+)\/)?$', cache_page(180 * 60)(RankingView.as_view())),
]
