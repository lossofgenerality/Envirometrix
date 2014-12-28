from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

from data.views import *
from analysis.views import *

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'},name="my_login"),
    
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
           
    url(r'^data/api/$', data_api),
    url(r'^data/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '%s/data' % settings.STATIC_ROOT, 'show_indexes': True}),
        
    url(r'^analysis/api/$', analysis_api),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '%s' % settings.MEDIA_ROOT, 'show_indexes': True}),
        
    url(r'^public/math$', math_gui),
    
    url(r'^output/(?P<user>.*)/$', output_index),
    url(r'^output/(?P<user>.*)/(?P<dir>.*)$', results_page),
    
        
    url(r'^', include(admin.site.urls)),
    
    
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

urlpatterns += staticfiles_urlpatterns()