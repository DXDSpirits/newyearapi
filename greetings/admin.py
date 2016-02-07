
from django.contrib import admin
from .models import Place, Greeting, Inspiration, Share, Relay


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'parent']
    search_fields = ['name', 'parent__name']


@admin.register(Greeting)
class GreetingAdmin(admin.ModelAdmin):
    def pfop_audio(self, request, queryset):
        for greeting in queryset:
            if greeting.statue == 'raw':
                greeting.perform_pfop()
    pfop_audio.short_description = "Pfop selected audio"

    def placelist(self, instance):
        return ', '.join([p.name for p in instance.places.all()])
    placelist.short_description = 'Places'

    def suit_row_attributes(self, obj, request):
        if obj.status == 'online':
            return {'class': 'success'}
        elif obj.status == 'raw':
            return {'class': 'error'}
        else:
            return {}

    def suit_cell_attributes(self, obj, column):
        style = 'word-break:break-all;'
        if True or column == 'url':
            style += 'max-width:160px;'
        return {'style': style}

    list_display = ['id', 'owner_id', 'time_created', 'status', 'key', 'url', 'description', 'placelist']
    filter_horizontal = ['places']
    actions = ['pfop_audio']


@admin.register(Inspiration)
class InspirationAdmin(admin.ModelAdmin):
    def placelist(self, instance):
        return ', '.join([p.name for p in instance.places.all()])
    placelist.short_description = 'Places'

    list_display = ['id', 'text', 'placelist']
    filter_horizontal = ['places']


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner_id', 'time_created']


@admin.register(Relay)
class RelayAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner_id', 'parent_id', 'time_created']
