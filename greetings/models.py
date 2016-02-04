
from django.db import models
from django.db.models.signals import post_save

from users.models import UserProfile

import requests
import jsonfield


class Place(models.Model):
    CATEGORY = (('province', 'Province'),
                ('city', 'City'),
                ('district', 'District'),)

    category = models.SlugField(choices=CATEGORY, default='city')
    parent = models.ForeignKey('self', blank=True, null=True)

    name = models.CharField(max_length=50, blank=True, null=True)

    data = jsonfield.JSONField(blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (unicode(self.name), self.category)


class Greeting(models.Model):
    STATUS = (('raw', 'Raw'),
              ('online', 'Online'),
              ('archived', 'Archived'),)

    owner_id = models.IntegerField(blank=True, null=True, db_index=True)
    time_created = models.DateTimeField(auto_now_add=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    status = models.SlugField(choices=STATUS, default='raw')
    key = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    url = models.URLField(blank=True, null=True)
    data = jsonfield.JSONField(blank=True, null=True)

    places = models.ManyToManyField(Place, blank=True, related_name="greetings")

    @property
    def profile(self):
        return UserProfile.objects.filter(user_id=self.owner_id).first()

    def __unicode__(self):
        return unicode(self.url)


def greeting_postsave(sender, instance, created, raw, **kwargs):
    if instance.status == 'online':
        Greeting.objects.filter(owner_id=instance.owner_id) \
                        .exclude(pk=instance.pk) \
                        .exclude(status='archived') \
                        .update(status='archived')
post_save.connect(greeting_postsave, sender=Greeting)


class Like(models.Model):
    owner_id = models.IntegerField(blank=True, null=True, db_index=True)
    time_created = models.DateTimeField(auto_now_add=True)

    greeting = models.ForeignKey(Greeting, blank=True, null=True)

    @property
    def profile(self):
        return UserProfile.objects.filter(user_id=self.owner_id).first()

    class Meta:
        unique_together = [['greeting', 'owner_id', ], ]


class Share(models.Model):
    owner_id = models.IntegerField(blank=True, null=True, db_index=True)
    time_created = models.DateTimeField(auto_now_add=True)


class Inspiration(models.Model):
    text = models.TextField(blank=True, null=True)
    places = models.ManyToManyField(Place, blank=True, related_name="inspirations",
                                    limit_choices_to={'category': 'province'})

    def __unicode__(self):
        return unicode(self.text)


class Relay(models.Model):
    owner_id = models.IntegerField(blank=True, null=True, unique=True)
    parent_id = models.IntegerField(blank=True, null=True, db_index=True)
    time_created = models.DateTimeField(auto_now_add=True)


def relay_postsave(sender, instance, created, raw, **kwargs):
    if created and instance.parent_id is not None:
        profile = UserProfile.objects.filter(user_id=instance.owner_id).first()
        greeting = Greeting.objects.filter(status='online', owner_id=instance.owner_id).first()
        if greeting is not None and profile is not None:
            province = greeting.places.get(category='province')
            url = 'http://testpayapi.wedfairy.com/api/v1/new_year/new_relation.json'
            params = {'api_key': 'f4c47fdb0a42dd2e4807716efaff039a17ea6d38'}
            data = {'user_id': instance.owner_id,
                    'parent_id': instance.parent_id,
                    'voice_id': greeting.id,
                    'nick_name': profile.name,
                    'avatar': profile.avatar,
                    'province_id': province.id,
                    'province_name': province.name}
            requests.post(url, json=data, params=params)
        Relay.objects.get_or_create(owner_id=instance.parent_id)
post_save.connect(relay_postsave, sender=Relay)
