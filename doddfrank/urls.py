
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

                       url(r'^organization\/list_of_orgs\/?$',
                           organization_cleanup_csv,
                           {},
                           name='doddfrank_organization_cleanup_csv'),

                       url(r'^organization\/(?P<organization_slug>[-\w]+)\/?$',
                           organization_detail,
                           {},
                           name='doddfrank_organization_detail'),

                       url(r'^agency/federal-reserve/?$',
                           'django.views.generic.simple.direct_to_template',
                           {'template': 'doddfrank/federal_reserve_takedown_notice.html'}),

                       url(r'^agency/sec/?$',
                           'django.views.generic.simple.direct_to_template',
                           {'template': 'doddfrank/sec_takedown_notice.html'}),

                       url(r'^agency/treasury/?$',
                           'django.views.generic.simple.direct_to_template',
                           {'template': 'doddfrank/treasury_takedown_notice.html'}),

                       url(r'^agency\/(?P<agency_slug>[-\w]+)\/?$',
                           agency_detail,
                           {},
                           name='doddfrank_agency_detail'),

                       url(r'^agency\/(?P<agency_slug>[-\w]+)\/(?P<id>\w+)\/?$',
                             meeting_detail,
                             {},
                             name='doddfrank_meeting_detail'),

                       url(r'^timeline\/?$',
                           'django.views.generic.simple.direct_to_template',
                           {'template': 'doddfrank/test_timeline.html', },
                           name='doddfrank_test_timeline'),

                       url(r'^widget\/?$',
                           meetings_widget,
                           {},
                           name='doddfrank_meetings_widget'),

                       url(r'^widget\.js',
                           'django.views.generic.simple.direct_to_template',
                           {'template': 'doddfrank/widget.js',
                            'mimetype': 'text/javascript',
                           },
                           name='doddfrank_meetings_widget_js')


)

