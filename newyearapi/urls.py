from django.conf.urls import patterns, include, url
from revproxy.views import ProxyView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/admin/', include(admin.site.urls)),

    url(r'^api/greetings/', include('greetings.urls')),
    url(r'^(?P<path>api/clients/.*)$', ProxyView.as_view(upstream='http://localhost:8000')),
)
