
from django.db import models
from django.db.models.signals import post_save

from users.models import UserProfile

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


class Inspiration(models.Model):
    text = models.TextField(blank=True, null=True)
    places = models.ManyToManyField(Place, blank=True, related_name="inspirations")

    def __unicode__(self):
        return unicode(self.text)
