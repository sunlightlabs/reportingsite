
from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

from doddfrank.views import *

urlpatterns = patterns('',

                       url(r'^\/?$',
                           index,
                           {},
                           name='doddfrank_index'),

                       url(r'^search\/?$',
                           search,
                           {},
                           name='doddfrank_search'),

                       url(r'^organization\/?$',
                           organization_list,
                           {},
                           name='doddfrank_organization_list'),

                       url(r'^organization\/(?P<organization_slug>[-\w]+)\/?$',
                           organization_detail,
                           {},
                           name='doddfrank_organization_detail'),

                       url(r'^agency\/(?P<agency_slug>[-\w]+)\/?$',
                           agency_detail,
                           {},
                           name='doddfrank_agency_detail'),

                       url(r'^agency\/(?P<agency_slug>[-\w]+)\/(?P<id>\w+)\/?$',
                             meeting_detail,
                             {},
                             name='doddfrank_meeting_detail')

)

