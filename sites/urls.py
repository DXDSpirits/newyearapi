from django.conf.urls import patterns, url, include
from rest_framework import routers
import apiviews
# from search import apiviews as search_apiviews

router = routers.DefaultRouter()

router.register(r'theme', apiviews.ThemeViewSet)
router.register(r'schema', apiviews.SchemaViewSet)
router.register(r'tip', apiviews.TipViewSet)
router.register(r'inspiration', apiviews.InspirationViewSet)
router.register(r'story', apiviews.StoryViewSet)
router.register(r'storyname', apiviews.StoryNameViewSet, base_name='story_name_retrieve')
router.register(r'storyevent', apiviews.StoryEventViewSet)
router.register(r'photo', apiviews.PhotoViewSet)
router.register(r'music', apiviews.MusicViewSet)
router.register(r'like', apiviews.LikeViewSet)
router.register(r'wish', apiviews.WishViewSet)

# router.register(r'universaltag', search_apiviews.UniversalTagViewSet, base_name='search_universaltag_legacy')
# router.register(r'storylist', search_apiviews.StoryViewSet, base_name='search_story_legacy')
# router.register(r'music', search_apiviews.MusicViewSet, base_name='search_music_legacy')

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
