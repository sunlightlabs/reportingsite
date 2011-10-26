from django.conf.urls.defaults import *

urlpatterns = patterns('findatcat.views',
    url(r'^$', 'index'),
    url(r'^browse/$', 'browse'),
)