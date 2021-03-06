import datetime
import itertools

from django.db.models import *
from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template

from tastypie.api import Api

from dateutil.relativedelta import relativedelta

from willard.models import *
from willard.feeds import *
from willard.views import *
from willard.api import *

cutoff = datetime.date.today() - relativedelta(months=12)
cutoff = datetime.date(year=cutoff.year,
                       month=cutoff.month,
                       day=1)


KEY_PREFIX = 'willard_12_'

urlpatterns = patterns('',

        url(r'^issue\/(?P<slug>[-\w]+)\.rss$',
            cache_page(GenericLobbyingFeed(), 60*60*24, key_prefix=KEY_PREFIX),
            {'model': Issue, },
            name='willard_issue_detail_feed'),

        url(r'^issue\/(?P<slug>[-\w]+)\.(?P<format>\w+)$',
            cache_page(detail_api, 60*5, key_prefix=KEY_PREFIX),
            {'model': Issue, },
            name='willard_issue_detail_api'),

        url(r'^issue\/(?P<slug>[-\w]+)\/?$',
            cache_page(issue_detail, 60*5, key_prefix=KEY_PREFIX),
         {},
         name='willard_issue_detail'),

        url(r'^issue\/(?P<slug>[-\w]+)\/all\/?$',
            cache_page(issue_detail_all, 60*5, key_prefix=KEY_PREFIX),
            {},
            name='willard_issue_detail_all'),

        url(r'^issue\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {
              'queryset': Issue.objects.order_by('issue'),
              },
            name='willard_issue_list'),

        url(r'^client\/(?P<slug>[-\w]+)\.rss$',
            cache_page(GenericLobbyingFeed(), 60*5, key_prefix=KEY_PREFIX),
            {'model': Client, },
            name='willard_client_detail_feed'),

        url(r'^client\/(?P<slug>[-\w]+)\.(?P<format>\w+)$',
            cache_page(detail_api, 60*5, key_prefix=KEY_PREFIX),
            {'model': Client, },
            name='willard_client_detail_api'),

        url(r'^client\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {
                'queryset': Client.objects.all(),
                'extra_context': {
                    'by_letter': [(letter, list(clients)) for letter, clients in itertools.groupby(Client.objects.all(), lambda x: x.display_name[0].upper())],
                    },
             },
            name='willard_client_list'),

        url(r'^firm\/(?P<slug>[-\w]+)\.rss$',
            cache_page(GenericLobbyingFeed(), 60*5, key_prefix=KEY_PREFIX),
            {'model': Registrant, },
            name='willard_registrant_detail_feed'),

        url(r'^firm\/(?P<slug>[-\w]+)\.(?P<format>\w+)$',
            cache_page(detail_api, 60*5, key_prefix=KEY_PREFIX),
            {'model': Registrant, },
            name='willard_registrant_detail_api'),

        url(r'^firm\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {
                'queryset': Registrant.objects.all(),
                'extra_context': {
                    'by_letter': [(letter, list(clients)) for letter, clients in itertools.groupby(Registrant.objects.all(), lambda x: x.display_name[0].upper())],
                    },
             },
            name='willard_registrant_list'),

        url(r'^firm\.(?P<format>\w+)$',
            object_list_api,
            {'model': Registrant,
                },
            name='willard_registrant_list_api'),

        url(r'^firm\/(?P<slug>[-\w]+)\/(?P<id>[-0-9A-Z]+)\/?$',
            cache_page(registration_detail, 60*5, key_prefix=KEY_PREFIX),
            {},
            name='willard_registration_detail'),

        url(r'^firm\/(?P<slug>[-\w]+)\/?$',
            cache_page(generic_detail_all, 60*5, key_prefix=KEY_PREFIX),
            {
                'model': Registrant,
                },
            name='willard_registrant_detail'),

        url(r'^client\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {'queryset': Client.objects.all()
                },
            name='willard_client_list'),

        url(r'^client\.(?P<format>\w+)$',
            object_list_api,
            {'model': Client,
                },
            name='willard_client_list_api'),

        url(r'^client\/(?P<slug>[-\w]+)\/?$',
            cache_page(generic_detail_all, 60*5, key_prefix=KEY_PREFIX),
            {
                'model': Client,
            },
            name='willard_client_detail'),

        url(r'^lobbyist\/(?P<slug>[-\w]+)\.rss$',
            cache_page(GenericLobbyingFeed(), 60*5, key_prefix=KEY_PREFIX),
            {'model': Lobbyist, },
            name='willard_lobbyist_detail_feed'),

        url(r'^lobbyist\/(?P<slug>[-\w]+)\.(?P<format>\w+)$',
            cache_page(detail_api, 60*5, key_prefix=KEY_PREFIX),
            {'model': Lobbyist, },
            name='willard_lobbyist_detail_api'),

        url(r'^lobbyist\/(?P<slug>[-\w]+)\/?$',
            object_detail,
            {
                'queryset': Lobbyist.objects.all(),
                'slug_field': 'slug',
            },
            name='willard_lobbyist_detail'),

        url(r'^lobbyist\/?$',
            lobbyist_list,
            {},
            name='willard_lobbyist_list'),

        url(r'^affiliated\/?$',
            object_list,
            {'queryset': AffiliatedOrganization.objects.all(),
             },
            name='willard_affiliated_list'),

        url(r'^affiliated\/(?P<slug>[-\w]+)?$',
            object_detail,
            {'queryset': AffiliatedOrganization.objects.all(),
             'slug_field': 'slug',
             },
            name='willard_affiliated_detail'),

        url(r'^all\.rss$',
            cache_page(RegistrationFeed(), 60*5, key_prefix=KEY_PREFIX),
            name='willard_feed'),

        url(r'^all\/?$',
            cache_page(registrations_all, 60*5, key_prefix=KEY_PREFIX),
            {},
            name='willard_registrations_all'),

        url(r'^search\/?$',
            cache_page(search, 60*5, key_prefix=KEY_PREFIX),
            {},
            name='willard_search'),

        url(r'^postemployment\/?$',
            cache_page(object_list, 60*15, key_prefix=KEY_PREFIX),
            {
                'queryset': PostEmploymentNotice.objects.filter(end_date__gte=datetime.date.today()).order_by('end_date'),
                'extra_context': {
                    'passed': PostEmploymentNotice.objects.filter(end_date__lt=datetime.date.today()).order_by('-end_date'), 
                    },
            },
            name='willard_postemployment_list'),

        url(r'^postemployment\.rss$',
            PostEmploymentFeed(),
            {},
            name='willard_postemployment_feed'),

        url(r'^postemployment\.(?P<format>\w+)$',
            cache_page(willard_postemployment_api, 60*15, key_prefix=KEY_PREFIX),
            {},
            name='willard_postemployment_api'),

        url(r'^registrations$',
            cache_page(registrations, 60*5, key_prefix=KEY_PREFIX),
            { },
            name='willard_registrations_home'),

        url(r'^registrations\/widget\/?$',
            cache_page(registrations_widget, 60*30, key_prefix=KEY_PREFIX),
            {},
            name='willard_registrations_widget'),

        url(r'^registrations\/widget\.js',
                direct_to_template,
                {'template': 'willard/widget.js', 
                 'mimetype': 'text/javascript',
                },
            name='willard_registrations_widget_js'),

        url(r'^fara\/(?P<object_id>\d+)\/?$',
            object_detail,
            {'queryset': ForeignLobbying.objects.all(), },
            name='willard_fara_filing'),

        url(r'^fara\/?$',
                object_list,
                {'queryset': ForeignLobbying.objects.order_by('-stamped'), 
                 'paginate_by': 50,
                },
                name='willard_fara_list'),

        url(r'^$',
            cache_page(index, 60*5, key_prefix=KEY_PREFIX),
            {},
            name='willard_index'),

)

# FARA API
v1_api = Api(api_name='v1')
v1_api.register(ForeignLobbyingResource())

urlpatterns += patterns('',
        (r'^fara\/api/', include(v1_api.urls))
)

