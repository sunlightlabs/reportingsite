import datetime
import itertools

from django.db.models import *
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail

from dateutil.relativedelta import relativedelta

from willard.models import *
from willard.feeds import *

cutoff = datetime.date.today() - relativedelta(months=12)
cutoff = datetime.date(year=cutoff.year,
                       month=cutoff.month,
                       day=1)


urlpatterns = patterns('',

        url(r'^issue\/(?P<slug>[-\w]+)\/rss\/?$',
         IssueFeed(),
         {},
         name='willard_issue_detail_feed'),

        url(r'^issue\/(?P<slug>[-\w]+)\/?$',
         'willard.views.issue_detail',
         {},
         name='willard_issue_detail'),

        url(r'^issue\/(?P<slug>[-\w]+)\/all\/?$',
            'willard.views.issue_detail_all',
            {},
            name='willard_issue_detail_all'),

        url(r'^issue\/?$',
            object_list,
            {
              'queryset': Issue.objects.order_by('issue'),
              },
            name='willard_issue_list'),

        url(r'^client\/(?P<slug>[-\w]+)\/rss\/?$',
         ClientFeed(),
         {},
         name='willard_client_detail_feed'),

        url(r'^client\/?$',
            object_list,
            {
                'queryset': Client.objects.all(),
                'extra_context': {
                    'by_letter': [(letter, list(clients)) for letter, clients in itertools.groupby(Client.objects.all(), lambda x: x.display_name[0].upper())],
                    },
             },
            name='willard_client_list'),

        url(r'^firm\/(?P<slug>[-\w]+)\/rss\/?$',
         RegistrantFeed(),
         {},
         name='willard_registrant_detail_feed'),

        url(r'^firm\/?$',
            object_list,
            {
                'queryset': Registrant.objects.all(),
                'extra_context': {
                    'by_letter': [(letter, list(clients)) for letter, clients in itertools.groupby(Registrant.objects.all(), lambda x: x.display_name[0].upper())],
                    },
             },
            name='willard_registrant_list'),

        url(r'^firm\/(?P<slug>[-\w]+)\/(?P<id>[-0-9A-Z]+)\/?$',
            'willard.views.registration_detail',
            {},
            name='willard_registration_detail'),

        url(r'^firm\/(?P<slug>[-\w]+)\/?$',
            'willard.views.generic_detail_all',
            {
                'model': Registrant,
                },
            name='willard_registrant_detail'),

        url(r'^client\/?$',
            object_list,
            {'queryset': Client.objects.all()
                },
            name='willard_client_list'),

        url(r'^client\/(?P<slug>[-\w]+)\/?$',
            'willard.views.generic_detail_all',
            {
                'model': Client,
            },
            name='willard_client_detail'),

        url(r'^rss\/?$',
            RegistrationFeed(),
            name='willard_feed'),

        url(r'^all\/?$',
            'willard.views.registrations_all',
            {},
            name='willard_registrations_all'),

        url(r'^search\/?$',
            'willard.views.search',
            {},
            name='willard_search'),

        url(r'^$',
            'willard.views.index',
            {},
            name='willard_index'),

)

