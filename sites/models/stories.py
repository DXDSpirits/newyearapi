from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.utils import timezone
from django.apps import apps as django_apps

from .schemas import Schema, SchemaSection
# from search.models import UniversalTag

import jsonfield
from helper import redis

redisclient = redis.get_client(db=0)


class StoryManager(models.Manager):
    def cloneStoryApps(self, storyapp_list, new_story):
        new_storyapps = []
        for new_storyapp in storyapp_list:
            new_storyapp.pk = None
            new_storyapp.story = new_story
            new_storyapp.owner = new_story.owner
            new_storyapps.append(new_storyapp)
        StoryApp = django_apps.get_model('appstore', 'StoryApp')
        StoryApp.objects.bulk_create(new_storyapps)

    def cloneStoryEvents(self, storyevent_list, new_story, datetime_now):
        new_storyevents = []
        for new_storyevent in storyevent_list:
            new_storyevent.pk = None
            new_storyevent.last_modified = datetime_now
            new_storyevent.story = new_story
            new_storyevent.owner = new_story.owner
            new_storyevents.append(new_storyevent)
        StoryEvent.objects.bulk_create(new_storyevents)

    def cloneStoryTags(self, storytag_list, new_story):
        new_story.tags.add(*list(storytag_list))

    def clone(self, origin, name, owner):
        datetime_now = timezone.now()
        origin_story_id = origin.pk
        new_story = Story.objects.get(pk=origin_story_id)
        storyevent_list = new_story.storyevent_set.filter(archived=False)
        storytag_list = new_story.tags.all()
        if new_story.featured == 3:  # prototype story
            storyapp_list = new_story.storyapp_set.filter(archived=False)
            new_story.prototype_id = origin_story_id
        else:
            storyapp_list = []
        new_story.parent_id = origin_story_id
        new_story.pk = None
        new_story.time_created = datetime_now
        new_story.last_modified = datetime_now
        new_story.featured = 0
        new_story.name = name
        new_story.owner = owner
        new_story.save_base(raw=True, force_insert=True)
        self.cloneStoryEvents(storyevent_list, new_story, datetime_now)
        self.cloneStoryApps(storyapp_list, new_story)
        self.cloneStoryTags(storytag_list, new_story)
        return new_story


class Story(models.Model):
    FEATURED = ((0, 'New'),
                (1, 'Finished'),
                (2, 'Featured'),
                (3, 'Prototype'),)

    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    prototype = models.ForeignKey('self', null=True, blank=True, related_name='inheritances')

    owner = models.ForeignKey(User, blank=True, null=True)

    name = models.SlugField(unique=True, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    schema = models.ForeignKey(Schema, blank=True, null=True)
    data = jsonfield.JSONField(blank=True, null=True)

    # theme = models.SlugField(blank=True, null=True)
    theme = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    css = models.TextField(blank=True, null=True)

    vendor = models.SlugField(blank=True, null=True)
    featured = models.IntegerField(default=0, db_index=True, choices=FEATURED)
    archived = models.BooleanField(default=False, db_index=True)
    legacy = models.BooleanField(default=False)

    last_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)

    objects = StoryManager()

    tags = models.ManyToManyField('search.UniversalTag', blank=True, limit_choices_to={'category__in': ['story', 'staff']})

    @property
    def progress(self):
        a = self.storyevent_set.filter(last_modified__gt=self.time_created).count()
        if self.last_modified > self.time_created:
            a += 1
        b = self.storyevent_set.count() + 1
        return '%.1f%%' % (a * 100 / b)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        app_label = 'sites'
        verbose_name_plural = 'Stories'


def story_postsave(sender, instance, created, raw, **kwargs):
    if created and not raw:
        story_events = [StoryEvent(story=instance, owner=instance.owner, name=schemasection, order=index+1)
                        for index, schemasection in enumerate(instance.schema.schemasection_set.all())]
        StoryEvent.objects.bulk_create(story_events)
    elif not created:
        story_events = instance.storyevent_set.exclude(owner=instance.owner)
        for story_event in story_events:
            story_event.owner = instance.owner
            story_event.save(update_fields=['owner'])
post_save.connect(story_postsave, sender=Story)


def flush_redis_story(sender, instance, created, raw, **kwargs):
    redisclient.delete('story:%s' % instance.name)
post_save.connect(flush_redis_story, sender=Story)


class StoryEvent(models.Model):
    owner = models.ForeignKey(User, blank=True, null=True)
    story = models.ForeignKey(Story, blank=True, null=True)

    schemasection = models.ForeignKey(SchemaSection, blank=True, null=True, verbose_name='Schema Section')

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    order = models.IntegerField(blank=True, null=True)
    data = jsonfield.JSONField(blank=True, null=True)

    archived = models.BooleanField(default=False, db_index=True)

    last_modified = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return self.schemasection.section.name

    def __unicode__(self):
        return unicode(self.story)

    class Meta:
        app_label = 'sites'
        index_together = (('story', 'order',),)
        ordering = ['story', 'order']


def attach_owner(sender, instance, raw, **kwargs):
    instance.owner = instance.story.owner
pre_save.connect(attach_owner, sender=StoryEvent)


def flush_redis_storyevent(sender, instance, created, raw, **kwargs):
    redisclient.delete('story:%s' % instance.story.name)
post_save.connect(flush_redis_storyevent, sender=StoryEvent)


class Photo(models.Model):
    owner = models.ForeignKey(User, blank=True, null=True)

    title = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    url = models.URLField(blank=True, null=True)
    path = models.ImageField(upload_to='photos', blank=True, null=True)

    time_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.url)

    class Meta:
        app_label = 'sites'


class Wish(models.Model):
    reply_to = models.ForeignKey('self', blank=True, null=True, related_name='replies')

    story = models.ForeignKey(Story, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)

    avatar = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    approved = models.BooleanField(default=True)

    time_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.message)

    class Meta:
        app_label = 'sites'


class Like(models.Model):
    story = models.ForeignKey(Story, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)

    time_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.story)

    class Meta:
        app_label = 'sites'
        unique_together = [['story', 'user', ], ]


class Statistics(models.Model):
    story = models.OneToOneField(Story, blank=True, null=True)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    visits = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.story)

    class Meta:
        app_label = 'sites'


def update_likes(sender, instance, created=False, **kwargs):
    story = instance.story
    count = story.like_set.count()
    Statistics.objects.update_or_create(story=story, defaults={'likes': count})
post_save.connect(update_likes, sender=Like)
post_delete.connect(update_likes, sender=Like)
