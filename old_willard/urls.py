import datetime

from django.db.models import *
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail

from willard.models import *
from willard.feeds import *


urlpatterns = patterns('',

        url(r'^issue\/(?P<code>\w{3})\/rss\/?$',
         IssueFeed(),
         {},
         name='willard_issue_detail_feed'),

        url(r'^issue\/(?P<code>\w{3})\/?$',
         'willard.views.issue_detail',
         {},
         name='willard_issue_detail'),

        url(r'^issue\/?$',
            object_list,
            {'queryset': IssueCode.objects.annotate(registration_count=Count('registration')).order_by('-registration_count'),
              },
            name='willard_issue_list'),

        url(r'^client\/?$',
            object_list,
            {'queryset': Client.objects.all(),
                },
            name='willard_client_list'),

        url(r'^firm\/?$',
            object_list,
            {'queryset': Organization.objects.annotate(registration_count=Count('registration')).order_by('-registration_count')
                },
            name='willard_organization_list'),

        url(r'^firm\/(?P<slug>[-\w]+)\/(?P<form_id>\d+)\/?$',
            'willard.views.registration_detail',
            {},
            name='willard_registration_detail'),

        url(r'^firm\/(?P<slug>[-\w]+)\/?$',
            'willard.views.organization_detail',
            {},
            name='willard_organization_detail'),

        url(r'^client\/?$',
            object_list,
            {'queryset': Client.objects.all()
                },
            name='willard_client_list'),

        url(r'^client\/(?P<slug>[-\w]+)\/?$',
            'willard.views.client_detail',
            {},
            name='willard_client_detail'),

        url(r'^date\/?$',
                'django.views.generic.date_based.archive_index',
                {'queryset': Registration.objects.all(),
                 'date_field': 'signed_date',
                },
                name='willard_date'),

        url(r'^date\/(?P<year>\d{4})\/?$',
                'django.views.generic.date_based.archive_year',
                {'queryset': Registration.objects.all(),
                 'date_field': 'signed_date',
                 },
                name='willard_date_year'),

        url(r'^date\/(?P<year>\d{4})\/(?P<month>\d\d?)\/?$',
                'django.views.generic.date_based.archive_month',
                {'queryset': Registration.objects.all(),
                 'date_field': 'signed_date',
                 'month_format': '%m',
                 },
                name='willard_date_month'),

        url(r'^date\/(?P<year>\d{4})\/(?P<month>\d\d?)\/(?P<day>\d\d?)\/?$',
                'django.views.generic.date_based.archive_day',
                {'queryset': Registration.objects.all(),
                 'date_field': 'signed_date',
                 'month_format': '%m',
                 },
                name='willard_date_day'),

        url(r'rss\/?$',
            RegistrationFeed(),
            name='willard_feed'),

        url(r'^$',
            'willard.views.index',
            {},
            name='willard_index'),

)

