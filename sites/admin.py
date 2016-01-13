
from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import Select, TextInput
from jsonfield.widgets import JSONWidget
from suit.widgets import AutosizedTextarea
from suit.admin import SortableTabularInline, SortableStackedInline

import models
from .upgrade_generic import upgrade_to_generic

import json
import random


@admin.register(models.Inspiration)
class InspirationAdmin(admin.ModelAdmin):
    def taglist(self, instance):
        return ', '.join([tag.title for tag in instance.tags.all()])
    taglist.short_description = "Tags"

    def text_formatted(self, instance):
        return u'<pre>%s</pre>' % instance.text
    text_formatted.allow_tags = True
    text_formatted.short_description = "Text"
    list_display = ['id', 'style', 'text_formatted', 'taglist', 'schemasection']
    list_filter = ['style']
    filter_horizontal = ['tags']


@admin.register(models.Music)
class MusicAdmin(admin.ModelAdmin):
    def play(self, instance):
        return u'<audio src="%s" preload="none" controls></audio>' % instance.url
    play.allow_tags = True
    play.short_description = "Play"

    def taglist(self, instance):
        return ' '.join([tag.title for tag in instance.tags.all()])
    taglist.short_description = "Tags"

    list_display = ['id', 'owner', 'title', 'taglist', 'url', 'play']
    filter_horizontal = ['tags']
    raw_id_fields = ['owner']


class ThemeOptionInline(admin.TabularInline):
    model = models.ThemeOption
    extra = 0
    fields = ['name', 'image']


class ThemeTuningInline(admin.TabularInline):
    class ThemeTuningInlineForm(ModelForm):
        class Meta:
            widgets = {
                'section': Select(attrs={'class': 'input-small'}),
                'category': Select(attrs={'class': 'input-small'}),
                'name': TextInput(attrs={'class': 'input-small'}),
                'title': TextInput(attrs={'class': 'input-small'}),
            }
    model = models.ThemeTuning
    extra = 0
    form = ThemeTuningInlineForm
    fields = [('section', 'category', 'name', 'title', 'image', 'is_default')]


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    class ThemeForm(ModelForm):
        class Meta:
            widgets = {
                'title': AutosizedTextarea(),
                'description': AutosizedTextarea(),
                'data': JSONWidget(attrs={'class': 'input-xxlarge', 'style': 'font-size: 13px;'})
            }

    def data_json(self, instance):
        return '<pre style="font-size:10px;max-height:200px;overflow:scroll;">%s</pre>' % json.dumps(instance.data, indent=4, ensure_ascii=False)
    data_json.allow_tags = True
    data_json.short_description = 'Data'

    def thumbnail(self, instance):
        return u'<img src="%s" style="max-width:100px;height:50px;" alt="" />' % instance.image
    thumbnail.allow_tags = True
    thumbnail.short_description = "Thumbnail"

    def schemalist(self, instance):
        return ', '.join([schema.name for schema in instance.schemas.all()])
    schemalist.short_description = "Schemas"

    list_display = ['id', 'name', 'thumbnail', 'title', 'schemalist', 'data_json']  # 'description', 'urlroot',
    list_display_links = ['id', 'name']
    inlines = [ThemeTuningInline, ThemeOptionInline]
    form = ThemeForm


@admin.register(models.ThemeTuning)
class ThemeTuningAdmin(admin.ModelAdmin):
    def thumbnail(self, instance):
        return u'<img src="%s" style="max-width:100px;height:50px;" alt="" />' % instance.image
    thumbnail.allow_tags = True
    thumbnail.short_description = "Image"

    list_display = ['id', 'section', 'category', 'name', 'title', 'thumbnail', 'is_default']
    list_display_links = ['id', 'name']
    list_filter = ['theme']


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'title', 'description']
    list_display_links = ['id', 'name']


@admin.register(models.SchemaSection)
class SchemaSectionAdmin(admin.ModelAdmin):
    def data_json(self, instance):
        return '<pre style="font-size:13px;">%s</pre>' % json.dumps(instance.data, indent=4, ensure_ascii=False)
    data_json.allow_tags = True
    data_json.short_description = 'Data'

    class SchemaSectionForm(ModelForm):
        class Meta:
            widgets = {
                'title': AutosizedTextarea(),
                'description': AutosizedTextarea(),
                'data': JSONWidget(attrs={'class': 'input-xxlarge', 'style': 'font-size: 13px;'})
            }

    class TipsInline(SortableTabularInline):
        class InlineForm(ModelForm):
            class Meta:
                widgets = {'text': AutosizedTextarea(attrs={'class': 'input-xxlarge'})}
        model = models.Tip
        extra = 0
        fields = ['style', 'text']
        form = InlineForm
        sortable = 'order'

    class InspirationsInline(TipsInline):
        model = models.Inspiration

    def thumbnail(self, instance):
        return u'<img src="%s" style="max-width:100px;height:50px;" alt="" />' % instance.image
    thumbnail.allow_tags = True
    thumbnail.short_description = "Thumbnail"

    list_display = ['id', 'schema', 'section', 'order', 'title', 'description', 'thumbnail', 'data_json']
    list_display_links = ['id', 'schema']
    list_filter = ['schema']
    inlines = [TipsInline, InspirationsInline]
    form = SchemaSectionForm


class SchemaSectionInline(SortableStackedInline):
    class SchemaSectionInlineForm(ModelForm):
        class Meta:
            widgets = {
                'title': AutosizedTextarea(),
                'description': AutosizedTextarea(),
                'data': JSONWidget(attrs={'class': 'input-xxlarge', 'style': 'font-size: 13px;'})
            }
    model = models.SchemaSection
    extra = 0
    fields = ['section', ('title', 'description'), 'data']
    form = SchemaSectionInlineForm
    sortable = 'order'


@admin.register(models.Schema)
class SchemaAdmin(admin.ModelAdmin):
    def data_json(self, instance):
        return '<pre style="font-size:12px;">%s</pre>' % json.dumps(instance.data, indent=4, ensure_ascii=False)
    data_json.allow_tags = True
    data_json.short_description = 'Data'

    def clone_schema(self, request, queryset):
        for schema in queryset:
            start = int('0xA00000', 16)
            end = int('0xFFFFFF', 16)
            num = random.randint(start, end)
            name = hex(num)[2:].lower()
            models.Schema.objects.clone(schema, name)
    clone_schema.short_description = "Clone selected Schema with a random name"

    class SchemaForm(ModelForm):
        class Meta:
            widgets = {
                'title': AutosizedTextarea(),
                'description': AutosizedTextarea(),
                'data': JSONWidget(attrs={'class': 'input-xxlarge', 'style': 'font-size: 13px;'})
            }

    class SchemaThemeInline(SortableStackedInline):
        model = models.SchemaTheme
        extra = 0
        sortable = 'order'

    def thumbnail(self, instance):
        return u'<img src="%s" style="max-width:100px;height:50px;" alt="" />' % instance.image
    thumbnail.allow_tags = True
    thumbnail.short_description = "Thumbnail"
    list_display = ['id', 'parent', 'name', 'title', 'description', 'data_json']
    list_display_links = ['id', 'name']
    inlines = [SchemaSectionInline, SchemaThemeInline]
    form = SchemaForm
    actions = ['clone_schema']


@admin.register(models.StoryEvent)
class StoryEventAdmin(admin.ModelAdmin):
    def data_json(self, instance):
        return '<pre style="font-size:13px;">%s</pre>' % json.dumps(instance.data, indent=4, ensure_ascii=False)
    data_json.allow_tags = True
    data_json.short_description = 'Data'
    list_display = ['id', 'owner', 'story', 'schemasection', 'title', 'description', 'archived', 'order', 'data_json']
    list_display_links = ['id', 'story']
    search_fields = ['data']
    raw_id_fields = ('owner', 'story')
    ordering = ('-id',)


class StoryEventInline(SortableStackedInline):
    class StoryEventInlineForm(ModelForm):
        class Meta:
            widgets = {
                'title': AutosizedTextarea(),
                'description': AutosizedTextarea(),
                'data': JSONWidget(attrs={'class': 'input-xxlarge', 'style': 'font-size: 13px;'})
            }
    model = models.StoryEvent
    extra = 0
    fields = [('schemasection', 'owner', 'archived'), ('title', 'description'), 'data']
    form = StoryEventInlineForm
    sortable = 'order'
    readonly_fields = ('owner',)


@admin.register(models.Story)
class StoryAdmin(admin.ModelAdmin):
    def clone_story(self, request, queryset):
        for story in queryset:
            start = int('0xA00000', 16)
            end = int('0xFFFFFF', 16)
            num = random.randint(start, end)
            name = hex(num)[2:].lower()
            models.Story.objects.clone(story, name, story.owner)
    clone_story.short_description = "Clone selected Story with a random name"

    def upgrade_story(self, request, queryset):
        for story in queryset:
            upgrade_to_generic(story)
    upgrade_story.short_description = "Upgrade selected Story to generic"

    class StoryForm(ModelForm):
        class Meta:
            widgets = {
                'title': AutosizedTextarea(),
                'description': AutosizedTextarea(),
                'css': AutosizedTextarea(),
                'data': JSONWidget(attrs={'class': 'input-xxlarge', 'style': 'font-size: 13px;'})
            }

    def suit_row_attributes(self, obj, request):
        if obj.schema is None:
            return {'class': 'error'}
        elif obj.featured > 0 and obj.featured < 3:
            return {'class': 'success'}
        elif obj.archived:
            return {'class': 'warning'}
        elif (obj.owner and obj.owner.username == 'prototype') or obj.featured == 3:
            return {'class': 'info'}
        else:
            return {}

    def desc_summary(self, instance):
        if instance.description is not None and len(instance.description) > 15:
            return instance.description[:15] + '...'
        else:
            return instance.description

    def taglist(self, instance):
        return ' '.join([tag.title for tag in instance.tags.all()])
    taglist.short_description = "Tags"

    desc_summary.short_description = 'Description'
    list_display = ['id', 'time_created', 'progress', 'owner', 'featured', 'archived', 'legacy',
                    'name', 'prototype', 'parent', 'title', 'desc_summary', 'schema', 'theme', 'taglist']
    list_display_links = ['id', 'name']
    list_filter = ['featured', 'vendor']
    search_fields = ['name', 'owner__username']
    inlines = [StoryEventInline]
    form = StoryForm
    actions = ['clone_story', 'upgrade_story']
    raw_id_fields = ('owner', 'prototype', 'parent')
    radio_fields = {'featured': admin.HORIZONTAL}
    filter_horizontal = ['tags']


@admin.register(models.Wish)
class WishAdmin(admin.ModelAdmin):
    def reply(self, instance):
        return instance.reply_to_id
    date_hierarchy = 'time_created'
    list_display = ['id', 'time_created', 'reply', 'approved', 'user', 'story', 'name', 'phone', 'email', 'message']
    list_display_links = ['id', 'story']
    search_fields = ['story__name']
    raw_id_fields = ('reply_to', 'user', 'story')


@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):
    date_hierarchy = 'time_created'
    list_display = ['id', 'time_created', 'user', 'story']
    search_fields = ['story__name', 'user__username']
    raw_id_fields = ('user', 'story')


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    def thumbnail(self, instance):
        return u'<img src="%s" style="max-width:100px;height:50px;" alt="" />' % instance.url
    thumbnail.allow_tags = True
    thumbnail.short_description = "Thumbnail"

    def thumbnail2(self, instance):
        if not instance.path:
            return ''
        else:
            return u'<img src="%s" style="max-width:100px;height:50px;" alt="" />' % instance.path.url
    thumbnail2.allow_tags = True
    thumbnail2.short_description = "Local Thumbnail"
    list_display = ['id', 'owner', 'title', 'thumbnail', 'url', 'thumbnail2']
    search_fields = ['url']
    raw_id_fields = ['owner']
