"""
Url configuration pointing to views handling minifiying
"""

from django.conf.urls.defaults import *

from dynamicsettings import views

urlpatterns = patterns('',
    url(r'^$', views.dynamicsettings_index, name='dynamicsettings_root'),
    url(r'^set/$', views.dynamicsettings_set, name='dynamicsettings_set'),
    url(r'^reset/$', views.dynamicsettings_reset, name='dynamicsettings_reset'),   
)