from django.conf.urls.defaults import *

urlpatterns = patterns('findatcat.views',
    url(r'^$', 'index', name='findatcat_index'),
    url(r'^browse/$', 'filter', name='findatcat_filter'),
    url(r'^(?P<slug>[\w\-]+)/$', 'category', name='findatcat_category'),
)