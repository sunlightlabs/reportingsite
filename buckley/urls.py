from django.conf.urls.defaults import *
from django.db.models import Sum

from buckley.models import *
from buckley.feeds import *


urlpatterns = patterns('',

        url(r'committee\/(?P<committee_slug>[-\w]+)\/(?P<object_id>\d+)\/?$',
            'buckley.views.expenditure_detail',
            {},
            name='buckley_expenditure_detail'),

        url(r'committee\/(?P<slug>[-\w]+)\/rss\/?$',
            CommitteeFeed(),
            name='buckley_committee_detail_feed'),

        url(r'committee\/(?P<committee_slug>[-\w]+)\/(?P<candidate_slug>[-\w]+)\/?$',
            'buckley.views.candidate_committee_detail',
            {},
            name='buckley_committee_candidate_detail'),

        url(r'committee/(?P<slug>[-\w]+)\/?$', 
            'django.views.generic.list_detail.object_detail', 
            {'queryset': Committee.objects.all(), },
            name='buckley_committee_detail'),

        url(r'committee\/?$',
            'django.views.generic.list_detail.object_list',
            {'queryset': Committee.objects.all(), },
            name='buckley_committee_list'),

        url(r'candidate\/(?P<slug>[-\w]+)\/rss\/?$',
            CandidateFeed(),
            name='buckley_candidate_detail_feed'),

        url(r'candidate\/(?P<candidate_slug>[-\w]+)\/(?P<committee_slug>[-\w]+)\/?$',
            'buckley.views.candidate_committee_detail',
            {},
            name='buckley_candidate_committee_detail'),

        url(r'candidate\/(?P<slug>[-\w]+)\/?$',
            'django.views.generic.list_detail.object_detail',
            {'queryset': Candidate.objects.all(), },
            name='buckley_candidate_detail'),

        url(r'candidate\/?$',
            'django.views.generic.list_detail.object_list',
            {'queryset': Candidate.objects.all(), },
            name='buckley_candidate_list'),

#        url(r'payee\/(?P<slug>[-\w]+)\/rss\/?$',
#            PayeeFeed(),
#            name='buckley_payee_detail_feed'),
#
#        url(r'payee\/(?P<slug>[-\w]+)\/?$',
#            'django.views.generic.list_detail.object_detail',
#            {'queryset': Payee.objects.all(), },
#            name='buckley_payee_detail'),
#
#        url(r'payee\/?$',
#            'django.views.generic.list_detail.object_list',
#            {'queryset': Payee.objects.annotate(total=Sum('expenditure__expenditure_amount')), },
#            name='buckley_payee_list'),

        url(r'race\/(?P<race>[-\w]+)\/?$',
            'buckley.views.race_expenditures',
            {},
            name='buckley_race_detail'),

        url(r'rss\/?$',
            ExpenditureFeed(),
            name='buckley_expenditures_feed'),

        url(r'widget\/?$',
            'buckley.views.widget',
            {},
            name='buckley_widget'),

        url(r'^\/?$',
            'django.views.generic.list_detail.object_list',
            {'queryset': Expenditure.objects.all(), 
             'template_name': 'buckley/index.html',
             'paginate_by': 25,
            },
            name='buckley_index'),

)
