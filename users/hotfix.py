
# from .models import User, UserProfile, WechatUser
from django.apps import AppConfig


def clear_wechat_user():
    WechatUser = AppConfig.get_model('WechatUser')
    for wechatuser in WechatUser.objects.filter(unionid__isnull=True):
        print wechatuser.id
        wechatuser.data = wechatuser.data or {}
        composer = wechatuser.data.setdefault('composer', {})
        composer['openid'] = wechatuser.openid
        wechatuser.openid = None
        wechatuser.save()


# def fix_user_profile():
#     for user in User.objects.all():
#         profile, created = UserProfile.objects.get_or_create(user=user)
#         print user.id
#         if hasattr(user, 'wechatuser'):
#             wechatuser = user.wechatuser
#             profile.avatar = wechatuser.data.get('headimgurl')
#             profile.name = wechatuser.data.get('nickname')
#             profile.save()

# def fix_unionid():
#     for wechatuser in WechatUser.objects.all():
#         if wechatuser.data:
#             unionid = wechatuser.data.get('unionid')
#             if unionid:
#                 wechatuser.unionid = unionid
#                 wechatuser.save(update_fields=['unionid'])

# def fix_wechatuserdata():
#     for wechatuser in WechatUser.objects.all():
#         if wechatuser.data:
#             wechatuser.data = { 'composer': wechatuser.data }
#         else:
#             wechatuser.data = {}
#         wechatuser.save(update_fields=['data'])
