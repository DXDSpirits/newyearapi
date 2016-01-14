from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/admin/', include(admin.site.urls)),

    url(r'^api/greetings/', include('greetings.urls')),
)
