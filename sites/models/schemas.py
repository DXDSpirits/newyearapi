
from search.models import UniversalTag

from django.db import models
import jsonfield


class Section(models.Model):
    name = models.SlugField(unique=True, blank=True, null=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    data = jsonfield.JSONField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        app_label = 'sites'


class SchemaManager(models.Manager):
    def clone(self, origin, name):
        origin_schema_sections = origin.schemasection_set.all()
        origin.pk = None
        origin.name = name
        origin.save()
        schema_sections = []
        for schemasection in origin_schema_sections:
            schemasection.pk = None
            schemasection.schema = origin
            schema_sections.append(schemasection)
        SchemaSection.objects.bulk_create(schema_sections)
        return origin


class Schema(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    name = models.SlugField(unique=True, blank=True, null=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    image = models.URLField(blank=True, null=True)

    data = jsonfield.JSONField(blank=True, null=True)

    @property
    def is_generic(self):
        return self.name == 'generic' or (self.parent is not None and self.parent.name == 'generic')

    objects = SchemaManager()

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        app_label = 'sites'


class SchemaSection(models.Model):
    schema = models.ForeignKey(Schema, blank=True, null=True)
    section = models.ForeignKey(Section, blank=True, null=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    image = models.URLField(blank=True, null=True)

    order = models.IntegerField(blank=True, null=True)
    data = jsonfield.JSONField(blank=True, null=True)

    def __unicode__(self):
        return '%s.%s' % (unicode(self.schema), unicode(self.section))

    class Meta:
        app_label = 'sites'
        index_together = [['schema', 'order', ], ]
        ordering = ['schema', 'order']


class Tip(models.Model):
    schemasection = models.ForeignKey(SchemaSection, blank=True, null=True)

    style = models.CharField(max_length=50, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    order = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.text)

    class Meta:
        app_label = 'sites'
        index_together = [['schemasection', 'order', ], ]
        ordering = ['schemasection', 'order']


class Inspiration(models.Model):
    schemasection = models.ForeignKey(SchemaSection, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    style = models.SlugField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    tags = models.ManyToManyField(UniversalTag, blank=True, limit_choices_to={'category__in': ['inspiration', 'story']})

    def __unicode__(self):
        return unicode(self.text)

    class Meta:
        app_label = 'sites'
        index_together = [['schemasection', 'order', ], ]
        ordering = ['schemasection', 'order']
