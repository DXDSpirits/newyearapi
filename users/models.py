
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import jsonfield


# @receiver(post_save, sender=get_user_model())
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True)

    avatar = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    data = jsonfield.JSONField(blank=True, null=True)

    last_modified = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class WechatUser(models.Model):
    user = models.OneToOneField(User, blank=True, null=True)
    openid = models.CharField(unique=True, max_length=200, blank=True, null=True)
    unionid = models.CharField(unique=True, max_length=200, blank=True, null=True)

    data = jsonfield.JSONField(blank=True, null=True)

    last_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=WechatUser)
def create_wechat_user(sender, instance=None, created=False, **kwargs):
    if created:
        wechatuser = instance
        username = 'wechat_user_%s' % wechatuser.id
        user = User.objects.create_user(username=username)
        wechatuser.user = user
        wechatuser.save()
        profile = user.userprofile
        wechatuserinfo = wechatuser.data.values()[0]
        profile.avatar = wechatuserinfo.get('headimgurl')
        profile.name = wechatuserinfo.get('nickname')
        profile.save()


class Referral(models.Model):
    user = models.OneToOneField(User, blank=True, null=True)
    source = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return self.source


class VerifyCode(models.Model):
    mobile = models.SlugField(unique=True, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)

    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.mobile


class SMS(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    sent = models.BooleanField(default=False)
    data = jsonfield.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'SMS'
        verbose_name_plural = 'SMS'


class ContactMessage(models.Model):
    sender = models.ForeignKey(User, blank=True, null=True)

    name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    reply = models.TextField(blank=True, null=True)

    time_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.message)
