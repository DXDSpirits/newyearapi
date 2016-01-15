
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from revproxy.views import ProxyView


urlpatterns = [
    url(r'^api/admin/', include(admin.site.urls)),
    url(r'^api/greetings/', include('greetings.urls')),
    url(r'^(?P<path>api/clients/.*)$', ProxyView.as_view(upstream=settings.AUTH_API_ROOT)),
    url(r'^(?P<path>api/users/.*)$', ProxyView.as_view(upstream=settings.AUTH_API_ROOT)),
]
