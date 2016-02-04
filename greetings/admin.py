
from django.contrib import admin
from .models import Place, Greeting, Inspiration, Share


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'parent']
    search_fields = ['name', 'parent__name']


@admin.register(Greeting)
class GreetingAdmin(admin.ModelAdmin):
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
