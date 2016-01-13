
from django.contrib.auth.models import User
from django.db import models
from search.models import UniversalTag


class Music(models.Model):
    owner = models.ForeignKey(User, blank=True, null=True)

    url = models.URLField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)

    time_created = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField(UniversalTag, limit_choices_to={'category__in': ['story', 'music_gene']})

    def __unicode__(self):
        return unicode(self.url)

    class Meta:
        app_label = 'sites'
