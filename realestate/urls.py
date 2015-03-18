from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
import settings
import autocomplete_light

autocomplete_light.autodiscover()
admin.autodiscover()

urlpatterns = patterns('',    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^estatebase/', include('estatebase.urls')),  
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',name='login'),     
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login',name='logout'),
    url(r'session_security/', include('session_security.urls')),
    url(r'^devrep/', include('devrep.urls')),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
