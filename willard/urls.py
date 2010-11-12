import datetime

from django.db.models import *
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail

from willard.models import *


urlpatterns = patterns('',

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

        url(r'^firm\/(?P<slug>[-\w]+)\/?$',
            object_detail,
            {'queryset': Organization.objects.all(),
                },
            name='willard_organization_detail'),

        url(r'^client\/?$',
            object_list,
            {'queryset': Client.objects.all()
                },
            name='willard_client_list'),

        url(r'^client\/(?P<slug>[-\w]+)\/?$',
            object_detail,
            {'queryset': Client.objects.all(),
                },
            name='willard_client_detail'),

        url(r'^$',
            'willard.views.index',
            {},
            name='willard_index'),

)

