
from django.db import models
import jsonfield


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    class Meta:
        db_table = 'auth_user'
        app_label = 'users'

    def __unicode__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.URLField()
    name = models.CharField()
    data = jsonfield.JSONField()
    last_modified = models.DateTimeField()

    class Meta:
        db_table = 'users_userprofile'
        app_label = 'users'

    def __unicode__(self):
        return self.name


class Token(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(User)
    created = models.DateTimeField()

    class Meta:
        db_table = 'authtoken_token'
        app_label = 'users'

    def __unicode__(self):
        return self.key
