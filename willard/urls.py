import datetime
import itertools

from django.db.models import *
from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from django.views.generic.list_detail import object_list, object_detail

from dateutil.relativedelta import relativedelta

from willard.models import *
from willard.feeds import *
from willard.views import *

cutoff = datetime.date.today() - relativedelta(months=12)
cutoff = datetime.date(year=cutoff.year,
                       month=cutoff.month,
                       day=1)


KEY_PREFIX = 'willard_2_'

urlpatterns = patterns('',

        url(r'^issue\/(?P<slug>[-\w]+)\.rss$',
            cache_page(GenericLobbyingFeed(), 60*60*24, key_prefix=KEY_PREFIX),
            {'model': Issue, },
            name='willard_issue_detail_feed'),

        url(r'^issue\/(?P<slug>[-\w]+)\.(?P<format>\w+)$',
            cache_page(detail_api, 60*60*24, key_prefix=KEY_PREFIX),
            {'model': Issue, },
            name='willard_issue_detail_api'),

        url(r'^issue\/(?P<slug>[-\w]+)\/?$',
            cache_page(issue_detail, 60*60*24, key_prefix=KEY_PREFIX),
         {},
         name='willard_issue_detail'),

        url(r'^issue\/(?P<slug>[-\w]+)\/all\/?$',
            cache_page(issue_detail_all, 60*60*24, key_prefix=KEY_PREFIX),
            {},
            name='willard_issue_detail_all'),

        url(r'^issue\/?$',
            cache_page(object_list, 60*60*24, key_prefix=KEY_PREFIX),
            {
              'queryset': Issue.objects.order_by('issue'),
              },
            name='willard_issue_list'),

        url(r'^client\/(?P<slug>[-\w]+)\.rss$',
            cache_page(GenericLobbyingFeed(), 60*60*24, key_prefix=KEY_PREFIX),
            {'model': Client, },
            name='willard_client_detail_feed'),

        url(r'^client\/(?P<slug>[-\w]+)\.(?P<format>\w+)$',
            cache_page(detail_api, 60*60*24, key_prefix=KEY_PREFIX),
            {'model': Client, },
            name='willard_client_detail_api'),

        url(r'^client\/?$',
            cache_page(object_list, 60*60*24, key_prefix=KEY_PREFIX),
            {
                'queryset': Client.objects.all(),
                'extra_context': {
                    'by_letter': [(letter, list(clients)) for letter, clients in itertools.groupby(Client.objects.all(), lambda x: x.display_name[0].upper())],
                    },
             },
            name='willard_client_list'),

        url(r'^firm\/(?P<slug>[-\w]+)\.rss$',
            cache_page(GenericLobbyingFeed(), 60*60*24, key_prefix=KEY_PREFIX),
            {'model': Registrant, },
            name='willard_registrant_detail_feed'),

        url(r'^firm\/(?P<slug>[-\w]+)\.(?P<format>\w+)$',
            cache_page(detail_api, 60*60*24, key_prefix=KEY_PREFIX),
            {'model': Registrant, },
            name='willard_registrant_detail_api'),

        url(r'^firm\/?$',
            cache_page(object_list, 60*60*24, key_prefix=KEY_PREFIX),
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
            cache_page(registration_detail, 60*60*24, key_prefix=KEY_PREFIX),
            {},
            name='willard_registration_detail'),

        url(r'^firm\/(?P<slug>[-\w]+)\/?$',
            cache_page(generic_detail_all, 60*60*24, key_prefix=KEY_PREFIX),
            {
                'model': Registrant,
                },
            name='willard_registrant_detail'),

        url(r'^client\/?$',
            cache_page(object_list, 60*60*24, key_prefix=KEY_PREFIX),
            {'queryset': Client.objects.all()
                },
            name='willard_client_list'),

        url(r'^client\.(?P<format>\w+)$',
            object_list_api,
            {'model': Client,
                },
            name='willard_client_list_api'),

        url(r'^client\/(?P<slug>[-\w]+)\/?$',
            cache_page(generic_detail_all, 60*60*24, key_prefix=KEY_PREFIX),
            {
                'model': Client,
            },
            name='willard_client_detail'),

        url(r'^lobbyist\/(?P<slug>[-\w]+)\.rss$',
            cache_page(GenericLobbyingFeed(), 60*60*24, key_prefix=KEY_PREFIX),
            {'model': Lobbyist, },
            name='willard_lobbyist_detail_feed'),

        url(r'^lobbyist\/(?P<slug>[-\w]+)\.(?P<format>\w+)$',
            cache_page(detail_api, 60*60*24, key_prefix=KEY_PREFIX),
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

        url(r'^all\.rss$',
            cache_page(RegistrationFeed(), 60*60*24, key_prefix=KEY_PREFIX),
            name='willard_feed'),

        url(r'^all\/?$',
            cache_page(registrations_all, 60*60*24, key_prefix=KEY_PREFIX),
            {},
            name='willard_registrations_all'),

        url(r'^search\/?$',
            cache_page(search, 60*60*24, key_prefix=KEY_PREFIX),
            {},
            name='willard_search'),

        url(r'^$',
            cache_page(index, 60*60*24, key_prefix=KEY_PREFIX),
            {},
            name='willard_index'),

)

