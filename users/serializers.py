
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import serializers
import re

from .models import ContactMessage, VerifyCode, Referral, UserProfile, WechatUser


mobile_no_re = re.compile(r'^1[0-9]{10}$')
def is_mobile_no(mobile_no):
    return mobile_no_re.match(mobile_no) is not None

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'avatar', 'data')


class WechatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WechatUser
        fields = ('id', 'openid', 'unionid')


class UserSerializer(serializers.ModelSerializer):
    def get_haspassword(self, obj):
        return obj.has_usable_password()
    username = serializers.CharField(max_length=64, required=True)
    password = serializers.CharField(max_length=64, required=True, write_only=True)
    #referral = serializers.CharField(max_length=64, required=False, write_only=True)
    referral = serializers.CharField(max_length=64, required=False)
    wechatuser = WechatUserSerializer(read_only=True)
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    haspassword = serializers.SerializerMethodField()

    def validate_username(self, value):
        if User.objects.filter(username = value).exists():
            raise serializers.ValidationError(_("Mobile number is taken"))
        if not is_mobile_no(value):
            raise serializers.ValidationError(_("Please input mobile number as username"))
        return value

    def validate_password(self, value):
        return value

    def update(self, user, validated_data):
        user.username = validated_data.get('username')
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def create(self, validated_data):
        user = User(username = validated_data.get('username'))
        user.set_password(validated_data.get('password'))
        user.save()
        referral = validated_data.get('referral')
        if referral:
            Referral.objects.create(user=user, source=referral)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email',
                  'referral', 'wechatuser', 'profile', 'haspassword')


class KanwawaUserCreationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=64, required=True)
    password = serializers.CharField(max_length=64, required=True, write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username = value).exists():
            raise serializers.ValidationError(_("Username is taken"))
        kanwawa_re = re.compile(r'^kanwawa_[0-9a-f]{10}$')
        if kanwawa_re.match(value) is None:
            raise serializers.ValidationError(_("Invalid username"))
        return value

    def validate_password(self, value):
        return value

    def create(self, validated_data):
        user = User(username = validated_data.get('username'))
        user.set_password(validated_data.get('password'))
        user.save()
        Referral.objects.create(user=user, source='kanwawa')
        return user

    class Meta:
        model = User
        fields = ('username', 'password')


class ForgetPasswordSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=64, required=True)

    def validate_mobile(self, value):
        if not User.objects.filter(username = value).exists():
            raise serializers.ValidationError(_("Mobile number can't be found"))
        if not is_mobile_no(value):
            raise serializers.ValidationError(_("Please input mobile number"))
        return value


class ResetPasswordSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=64, required=True)
    code = serializers.CharField(max_length=64, required=True)
    password = serializers.CharField(max_length=64, required=True)

    def validate_mobile(self, value):
        if not User.objects.filter(username = value).exists():
            raise serializers.ValidationError(_("Mobile number can't be found"))
        if not is_mobile_no(value):
            raise serializers.ValidationError(_("Please input mobile number"))
        return value

    def validate_password(self, value):
        return value

    def validate(self, data):
        verifyCode = VerifyCode.objects.filter(mobile = data['mobile'])
        if not verifyCode.exists() or verifyCode.first().code != data['code']:
            raise serializers.ValidationError(_("Verify code is wrong"))
        return data


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ('id', 'user', 'name', 'phone', 'email', 'message')
