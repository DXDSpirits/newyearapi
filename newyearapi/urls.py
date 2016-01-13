from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/api-token-auth/', 'users.apiviews.obtain_auth_token'),

    url(r'^api/users/', include('users.urls')),
    url(r'^api/sites/', include('sites.urls')),

    url(r'^api/appstore/', include('appstore.urls')),
    url(r'^api/search/', include('search.urls')),

    url(r'^api/staff/', include('staff.urls')),
    url(r'^api/clients/', include('clients.urls')),

    url(r'^api/vendors/', include('vendors.urls')),

    url(r'^api/notifications/', include('notifications.urls')),
)


from django.conf import settings
try:
    if settings.LOCAL_SETTINGS and settings.DEBUG:
        from django.conf.urls.static import static
        urlpatterns += static('/media/', document_root = settings.MEDIA_ROOT)
except:
    pass
