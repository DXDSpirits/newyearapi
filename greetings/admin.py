
from django.contrib import admin
from .models import Place, Greeting


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'parent']


@admin.register(Greeting)
class GreetingAdmin(admin.ModelAdmin):
    def placelist(self, instance):
        return ', '.join([p.name for p in instance.places.all()])
    placelist.short_description = "Places"

    list_display = ['id', 'owner_id', 'time_created', 'key', 'url', 'placelist']
    filter_horizontal = ['places']
