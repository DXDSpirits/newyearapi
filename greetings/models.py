
from django.db import models
from users.models import UserProfile

import jsonfield


class Place(models.Model):
    CATEGORY = (('province', 'Province'),
                ('city', 'City'),
                ('district', 'District'),)

    category = models.SlugField(blank=True, null=True, choices=CATEGORY)
    parent = models.ForeignKey('self', blank=True, null=True)

    name = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return u'%s (%s)' % (unicode(self.name), self.category)


class Greeting(models.Model):
    owner_id = models.IntegerField()
    time_created = models.DateTimeField(auto_now_add=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    key = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    url = models.URLField(blank=True, null=True)
    data = jsonfield.JSONField(blank=True, null=True)

    places = models.ManyToManyField(Place, blank=True)

    @property
    def profile(self):
        return UserProfile.objects.filter(user_id=self.owner_id).first()

    def __unicode__(self):
        return unicode(self.url)
