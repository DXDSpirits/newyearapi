from django.conf.urls import patterns, url, include
from rest_framework import routers
import apiviews

router = routers.DefaultRouter()

router.register(r'user', apiviews.UserViewSet)
router.register(r'kanwawauser', apiviews.KanwawaUserViewSet, base_name='kanwawa-user')

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^report_online/$', apiviews.ReportOnline.as_view()),
    url(r'^forget_password/$', apiviews.ForgetPassword.as_view()),
    url(r'^reset_password/$', apiviews.ResetPassword.as_view()),
    url(r'^contactmessage/', apiviews.ContactMessageCreate.as_view()),
    url(r'^wechat-auth-url/', apiviews.WechatAuthURL.as_view()),
    url(r'^wechat-auth/', apiviews.WechatAuth.as_view()),
    url(r'^wechat-openid/', apiviews.WechatOpenID.as_view()),
    url(r'^profile/(?P<pk>[0-9]+)/$', apiviews.UserProfileViewSet.as_view()),
)
