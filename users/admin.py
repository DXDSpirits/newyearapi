import json

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token

import models
from utils.sms import send_sms


class CustomUserAdmin(UserAdmin):
    class UserProfileInline(admin.TabularInline):
        model = models.UserProfile
        extra = 0

    class WechatUserInline(admin.TabularInline):
        model = models.WechatUser
        extra = 0

    def referral_source(self, instance):
        return instance.referral.source
    # list_display = UserAdmin.list_display + ('date_joined', 'last_login', 'referral',)
    list_display = ('id', 'username', 'date_joined', 'last_login', 'referral_source', 'email', 'first_name', 'last_name',)
    list_display_links = ('id', 'username')
    ordering = ('-id',)
    list_filter = ('groups__name', 'date_joined', 'last_login', 'referral__source')
    inlines = [UserProfileInline, WechatUserInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class CustomTokenAdmin(TokenAdmin):
    search_fields = ['user__username']

admin.site.unregister(Token)
admin.site.register(Token, CustomTokenAdmin)


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def data_json(self, instance):
        return '<pre style="font-size:12px;">%s</pre>' % json.dumps(instance.data, indent=4, ensure_ascii=False)
    data_json.allow_tags = True
    data_json.short_description = 'Data'

    def avatar_thumbnail(self, instance):
        return u'<img src="%s" style="max-width:100px;height:50px;" alt="" />' % instance.avatar
    avatar_thumbnail.allow_tags = True
    avatar_thumbnail.short_description = "Avatar"

    def user_link(self, instance):
        return '<a href="/admin/auth/user/%d">%s</a>' % (instance.user.id, instance.user)
    user_link.allow_tags = True
    user_link.short_description = 'User'
    list_display = ['id', 'user_link', 'name', 'avatar_thumbnail', 'data_json']
    raw_id_fields = ('user',)
    search_fields = ['name']


@admin.register(models.WechatUser)
class WechatUserAdmin(admin.ModelAdmin):
    def data_json(self, instance):
        return '<pre style="font-size:12px;">%s</pre>' % json.dumps(instance.data, indent=4, ensure_ascii=False)
    data_json.allow_tags = True
    data_json.short_description = 'Data'

    def user_link(self, instance):
        return '<a href="/admin/auth/user/%d">%s</a>' % (instance.user.id, instance.user)
    user_link.allow_tags = True
    user_link.short_description = 'User'

    list_display = ['id', 'user_link', 'openid', 'unionid', 'data_json']
    raw_id_fields = ('user',)


@admin.register(models.ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['time_created', 'name', 'phone', 'email', 'message', 'reply']


@admin.register(models.VerifyCode)
class VerifyCodeAdmin(admin.ModelAdmin):
    list_display = ['mobile', 'code', 'last_modified']


@admin.register(models.Referral)
class ReferralAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ['user', 'source']


@admin.register(models.SMS)
class SMSAdmin(admin.ModelAdmin):
    def data_json(self, instance):
        return '<pre style="font-size:13px;">%s</pre>' % json.dumps(instance.data, indent=4, ensure_ascii=False)
    data_json.allow_tags = True
    data_json.short_description = 'Data'

    def send_sms(self, request, queryset):
        for sms in queryset:
            send_sms(sms)
    send_sms.short_description = "Send SMS"
    list_display = ['user', 'sent', 'data_json']
    actions = ['send_sms']
