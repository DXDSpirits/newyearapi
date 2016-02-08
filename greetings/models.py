
# coding=utf8

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.six.moves.urllib import parse as urlparse

from users.models import UserProfile

from qiniu import Auth, PersistentFop, op_save

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

    def perform_pfop(self, origin):
        access_key = settings.QINIU['ACCESS_KEY']
        secret_key = settings.QINIU['SECRET_KEY']
        path = reverse('greetings-pfop-notify')
        notify_url = urlparse.urljoin(origin, path)

        auth = Auth(access_key, secret_key)
        pfop = PersistentFop(auth, 'tatmusic', 'wechataudio', notify_url)
        op = op_save('avthumb/mp3', 'tatmusic', self.key + '.mp3')
        ret, info = pfop.execute(self.key, [op])
        if self.data is None:
            self.data = ret
        else:
            self.data.update(ret)
        self.save(update_fields=['data'])

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

    @property
    def profile(self):
        return UserProfile.objects.filter(user_id=self.owner_id).first()


API_ROOT = 'http://testpayapi.wedfairy.com/api/v1/new_year/'
API_KEY = 'f4c47fdb0a42dd2e4807716efaff039a17ea6d38'
FAKE = {355784: 16, 9387: 10, 364982: 14, 364950: 12, 306406: 10, 15546: 8}


def relay_postsave(sender, instance, created, raw, **kwargs):
    if created and instance.parent_id is not None:
        profile = UserProfile.objects.filter(user_id=instance.owner_id).first()
        greeting = Greeting.objects.filter(owner_id=instance.owner_id).last()
        if greeting is not None and profile is not None and instance.owner_id != instance.parent_id:
            province = greeting.places.get(category='province')
            url = API_ROOT + 'new_relation.json'
            params = {'api_key': API_KEY}
            data = {'user_id': instance.owner_id,
                    'parent_id': instance.parent_id,
                    'voice_id': greeting.id,
                    'nick_name': profile.name,
                    'avatar': profile.avatar,
                    'province_id': province.id,
                    'province_name': province.name}
            requests.post(url, json=data, params=params)
        Relay.objects.get_or_create(owner_id=instance.parent_id, defaults={'parent_id': 0})
post_save.connect(relay_postsave, sender=Relay)


def transform_rank(item):
    greeting_id = item.get('voice_id')
    user_id = item.get('user_id')
    avatar = item.get('avatar')
    name = item.get('nick_name')
    count = item.get('children_count', 0)
    if user_id <= 0 or name is None:
        count = 0
    count += FAKE.get(user_id, 0)
    return {'greeting_id': greeting_id, 'user_id': user_id, 'avatar': avatar, 'name': name, 'count': count}


def get_relay_ranking():
    url = API_ROOT + 'relations/rank.json'
    params = {'api_key': API_KEY}
    r = requests.get(url, params=params)
    ranking = [transform_rank(i) for i in r.json()]
    addition = [(u'阿亮', 42), (u'NAKADA', 53), (u'雪妍★', 45), (u'艾莉丝丝丝', 39),
                (u'徐铮', 32), (u'梓桐', 27), (u'Fang', 29), (u'小Lea', 36)]
    ranking.extend([{'name': name, 'count': count} for name, count in addition])
    ranking = sorted(ranking, key=lambda item: -item['count'])[:15]
    return ranking


def get_relays(user_id):
    url = API_ROOT + ('relations/%d/children.json' % user_id)
    params = {'api_key': API_KEY}
    r = requests.get(url, params=params)
    data = r.json()
    count = len(data) if isinstance(data, list) else 0
    count += FAKE.get(user_id, 0)
    return {'count': count}
