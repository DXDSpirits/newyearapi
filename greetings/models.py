
from django.db import models


class Place(models.Model):
    CATEGORY = (('province', 'Province'),
                ('city', 'City'),
                ('district', 'District'),)

    category = models.SlugField(blank=True, null=True, choices=CATEGORY)
    parent = models.ForeignKey('self', blank=True, null=True)

    name = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)


class Greeting(models.Model):
    owner_id = models.IntegerField()

    place = models.ForeignKey(Place, blank=True, null=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    url = models.URLField(blank=True, null=True)

    time_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.url)
