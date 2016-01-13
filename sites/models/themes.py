
from django.db import models
from django.db.models.signals import post_save
from schemas import Schema
import jsonfield

from helper import redis

redisclient = redis.get_client(db=0)


class Theme(models.Model):
    name = models.SlugField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    urlroot = models.URLField(blank=True, null=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    data = jsonfield.JSONField(blank=True, null=True)

    schemas = models.ManyToManyField(Schema, through='SchemaTheme')

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        app_label = 'sites'


def flush_redis_theme(sender, instance, created, raw, **kwargs):
    redisclient.delete('theme:%s' % instance.name)
post_save.connect(flush_redis_theme, sender=Theme)


class ThemeOption(models.Model):
    theme = models.ForeignKey(Theme, blank=True, null=True)
    name = models.SlugField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return '%s[%s]' % (unicode(self.theme), unicode(self.name))

    class Meta:
        app_label = 'sites'


class ThemeTuning(models.Model):
    TUNING_SECTION = (('all', 'All'),
                      ('photo', 'Photo'),
                      ('people', 'People'),
                      ('article', 'Article'),
                      ('gallery', 'Gallery'),
                      ('timeline', 'Timeline'),
                      ('weddinghero', 'Wedding Hero'),
                      ('viewport', 'Viewport'),)

    TUNING_CATEGORY = (('layout', 'Layout'),
                       ('color', 'Color'),
                       ('type', 'Type'),)

    theme = models.ForeignKey(Theme, blank=True, null=True)

    section = models.SlugField(blank=True, null=True, db_index=False, choices=TUNING_SECTION)
    category = models.SlugField(blank=True, null=True, db_index=False, choices=TUNING_CATEGORY)

    name = models.SlugField(blank=True, null=True, db_index=False)
    title = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)

    is_default = models.BooleanField(default=False)

    data = jsonfield.JSONField(blank=True, null=True)

    def __unicode__(self):
        return '.'.join([unicode(self.theme), self.section, self.category, self.name])

    class Meta:
        app_label = 'sites'
        index_together = (('theme', 'section', 'category'),)
        ordering = ['theme', 'section', 'category']


class SchemaTheme(models.Model):
    theme = models.ForeignKey(Theme)
    schema = models.ForeignKey('Schema')
    order = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.theme)

    class Meta:
        app_label = 'sites'
