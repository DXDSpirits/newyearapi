
import random
import base64
import simplejson as json
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from rest_framework import generics, views, permissions, response, decorators, viewsets, mixins, status, throttling
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from sites.models import Story, StoryEvent, Photo, Wish

from .models import ContactMessage, VerifyCode, WechatUser, UserProfile, Referral
from .utils.sms import send_verify_code
from .permissions import IsSelfOrIsNew, IsOwner
from .serializers import ContactMessageSerializer, ResetPasswordSerializer, ForgetPasswordSerializer, \
                         UserProfileSerializer, KanwawaUserCreationSerializer, UserSerializer

from weixin.client import WeixinMpAPI

from helper import redis
import logging


redisclient = redis.get_client(db=0)
logger = logging.getLogger('apps')


class WechatAuthURL(views.APIView):
    def get(self, request):
        scope = ("snsapi_userinfo", )
        wechat_app = settings.WECHAT_APP['composer']
        api = WeixinMpAPI(appid=wechat_app['APP_ID'],
                          app_secret=wechat_app['APP_SECRET'],
                          redirect_uri='http://api.wedfairy.com/api/users/wechat-auth/')
        authorize_url = api.get_authorize_url(scope=scope)
        return response.Response({'authorize_url': authorize_url})


class WechatAuth(views.APIView):
    def get_or_create_user(self, userinfo, platform, referral):
        openid = userinfo['openid']
        unionid = userinfo['unionid']
        wechatuser = WechatUser.objects.filter(unionid=unionid).first()
        if wechatuser is None:
            wechatuser = WechatUser.objects.create(openid=(openid if platform == 'composer' else None),
                                                   unionid=unionid, data={platform: userinfo})
            if referral:
                Referral.objects.create(user=wechatuser.user, source=referral)
        else:
            if platform == 'composer':
                wechatuser.openid = openid
            wechatuser.data[platform] = userinfo
            wechatuser.save()
        return wechatuser

    def redirect_url(self, state, token=None):
        platform = state.get('platform')
        durl = 'http://story.wedfairy.com' if platform in {'composer', 'hybrid'} else 'http://www.wedfairy.com'
        url = state.get('origin', durl)
        if token is not None:
            url += ('/corslogin/%s' % token)
        return url

    def get(self, request):
        code = request.query_params.get('code')
        state = self.parse_state(request.query_params.get('state'))
        platform = state.get('platform')
        referral = state.get('referral')
        if code and platform:
            userinfo = self.fetch_userinfo(platform, code)
            if userinfo is not None and 'openid' in userinfo and 'unionid' in userinfo:
                wechatuser = self.get_or_create_user(userinfo, platform, referral)
                token, created = Token.objects.get_or_create(user=wechatuser.user)
                location = self.redirect_url(state, token.key)
                return response.Response(headers={'Location': location}, status=status.HTTP_301_MOVED_PERMANENTLY)
        location = self.redirect_url(state)
        return response.Response(headers={'Location': location}, status=status.HTTP_301_MOVED_PERMANENTLY)

    def fetch_userinfo(self, platform, code):
        code_key = 'authcode:%s' % code
        userinfo_in_vault = redisclient.get(code_key)
        if userinfo_in_vault is not None:
            return json.loads(userinfo_in_vault)
        try:
            wechat_app = settings.WECHAT_APP[platform]
            api = WeixinMpAPI(appid=wechat_app['APP_ID'], app_secret=wechat_app['APP_SECRET'])
            auth_info = api.exchange_code_for_access_token(code=code)
            openid = auth_info.get('openid')
            access_token = auth_info.get('access_token')
            api = WeixinMpAPI(access_token=access_token)
            userinfo = api.user(openid=openid)
            redisclient.setex(code_key, 3600, json.dumps(userinfo, ensure_ascii=False))
            return userinfo
        except Exception as e:
            logger.error('Fetch Wechat Userinfo Failed. %s.' % e, extra={'request': self.request})
            return None

    def parse_state(self, state_str):
        if state_str == 'hybrid|ios':
            return {'platform': 'hybrid', 'referral': 'ios'}
        else:
            try:
                state_json = base64.b64decode(state_str)
                data = json.loads(state_json)
                return data
            except Exception as e:
                logger.error('Wechat Auth State Wrong: %s.' % e, extra={'request': self.request})
                return {}

    def parse_state_legacy(self, state_str):
        state = state_str.split('|') if state_str else []
        platform = state[0] if len(state) > 0 else None
        referral = state[1] if len(state) > 1 else None
        return platform, referral


class WechatOpenID(views.APIView):
    def get(self, request):
        location = 'http://testpay.wedfairy.com/pricing/?openid=%s'
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        openid = self.fetch_openid(code) if code and state == 'wx_pub_pay_pricing' else ''
        return response.Response(headers={'Location': location % openid},
                                 status=status.HTTP_301_MOVED_PERMANENTLY)

    def fetch_openid(self, code):
        try:
            wechat_app = settings.WECHAT_APP['composer']
            api = WeixinMpAPI(appid=wechat_app['APP_ID'], app_secret=wechat_app['APP_SECRET'])
            auth_info = api.exchange_code_for_access_token(code=code)
            openid = auth_info.get('openid')
            return openid
        except Exception as e:
            logger.error('Fetch Wechat OpenID Failed. %s.' % e, extra={'request': self.request})
            return None


class UserProfileViewSet(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsOwner,)


# class UserViewSet(viewsets.ModelViewSet):
class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  # mixins.UpdateModelMixin,
                  # mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelfOrIsNew,)

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

    @decorators.list_route(methods=['post', 'patch'],
                           permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        password = request.data.get('password')
        if password is not None:
            user = request.user
            user.set_password(password)
            user.save(update_fields=['password'])
            serializer = UserSerializer(user, context={'request': request})
            return response.Response(serializer.data)
        else:
            return response.Response()


class KanwawaUserThrottle(throttling.UserRateThrottle):
    rate = '5/second'


class KanwawaUserViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = User.objects.filter(referral__source='kanwawa')
    serializer_class = KanwawaUserCreationSerializer
    permission_classes = (IsSelfOrIsNew,)
    throttle_classes = (KanwawaUserThrottle,)

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)


class ObtainAuthToken(views.APIView):
    throttle_classes = ()
    permission_classes = ()
    serializer_class = AuthTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        now = timezone.now()
        dur = now - token.created
        sec = (60*60*24*7) - (dur.total_seconds() % (60*60*24*7))
        expires = now + timedelta(seconds=sec)
        return response.Response({'token': token.key,
                                  'expires': expires})
obtain_auth_token = ObtainAuthToken.as_view()


class ReportOnline(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = request.user
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return response.Response()


class ForgetPassword(generics.CreateAPIView):
    serializer_class = ForgetPasswordSerializer

    def perform_create(self, serializer):
        mobile = serializer.data['mobile']
        verifyCode, created = VerifyCode.objects.get_or_create(mobile=mobile)
        if created or verifyCode.last_modified + timedelta(hours=1) < datetime.now():
            verifyCode.code = random.randint(1000, 9999)
            verifyCode.save(update_fields=['code', 'last_modified'])
            send_verify_code(mobile, verifyCode.code)


class ResetPassword(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer

    def perform_create(self, serializer):
        mobile = serializer.data['mobile']
        user = User.objects.get(username=mobile)
        user.set_password(serializer.data['password'])
        user.save(update_fields=['password'])
        VerifyCode.objects.filter(mobile=mobile).update(code=None)


class ContactMessageCreate(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
