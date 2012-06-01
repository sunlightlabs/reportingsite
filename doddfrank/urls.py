
from django.conf.urls.defaults import *

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

                       url(r'agency/(?P<agency_slug>[-\w]+)/topics/(?P<year>\d{4})/?$',
                           agency_topic_xtab, 
                           {},
                           name='doddfrank_agency_topic_xtab'),

                       url(r'agency/(?P<agency_slug>[-\w]+)/topics/?$',
                           agency_topic_freq,
                           {},
                           name='doddfrank_agency_topics'),

                       url(r'agency/frequency/?$',
                           agency_meeting_freq_table,
                           {},
                           name='doddfrank_agency_frequency'),

                       url(r'^organization/frequency\/?$',
                           organization_frequency_table,
                           {},
                           name='doddfrank_organization_frequency'),

                       url(r'^organization\/list_of_orgs\/?$',
                           organization_cleanup_csv,
                           {},
                           name='doddfrank_organization_cleanup_csv'),

                       url(r'^organization\/(?P<organization_id>[\d]+)\/?$',
                           organization_detail,
                           {},
                           name='doddfrank_organization_detail_unamb'),

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

