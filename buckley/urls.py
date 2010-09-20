from django.conf.urls.defaults import *
from django.db.models import Sum
from django.views.decorators.cache import cache_page
from django.views.generic.list_detail import object_list, object_detail

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
            cache_page(object_detail, 60*15),
            #'django.views.generic.list_detail.object_detail', 
            {'queryset': Committee.objects.all(), },
            name='buckley_committee_detail'),

        url(r'committee\/?$',
            object_list,
            #'django.views.generic.list_detail.object_list',
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
            cache_page(object_detail, 60*15),
            #'django.views.generic.list_detail.object_detail',
            {'queryset': Candidate.objects.all(), },
            name='buckley_candidate_detail'),

        url(r'candidate\/?$',
            cache_page(object_list, 60*15),
            #'django.views.generic.list_detail.object_list',
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

        url(r'race\/(?P<race>[-\w]+)\/(?P<election_type>[-\w]+)\/?$',
            'buckley.views.race_expenditures',
            {},
            name='buckley_race_election_type_detail'),

        url(r'race\/?$',
            'buckley.views.race_list',
            {},
            name='buckley_race_list'),

        url(r'^rss\/?$',
            ExpenditureFeed(),
            name='buckley_expenditures_feed'),

        url(r'widget\/?$',
            'buckley.views.widget',
            {},
            name='buckley_widget'),

        url(r'embed\/?$',
            'buckley.views.embed',
            {},
            name='buckley_embed'),

        url(r'about\/?$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'buckley/about.html', },
            name='buckley_about'),

        url(r'letters\/?$',
            cache_page(object_list, 60*60),
            #'django.views.generic.list_detail.object_list',
            {'queryset': IEOnlyCommittee.objects.all(), },
            name='buckley_letter_list'),

        url(r'letters\/rss\/?$',
            CommitteeLetterFeed(),
            name='buckley_letter_feed'),

        url(r'letters\/(?P<object_id>C\d+)\/?$',
            object_detail,
            #'django.views.generic.list_detail.object_detail',
            {'queryset': IEOnlyCommittee.objects.all(), },
            name='buckley_letter_detail'),

        url(r'search\/?$',
            'buckley.views.search',
            {},
            name='buckley_search'),

        url(r'^\/?$',
            cache_page(object_list, 60*15),
            #'django.views.generic.list_detail.object_list',
            {'queryset': Expenditure.objects.all(), 
             'template_name': 'buckley/index.html',
             'paginate_by': 25,
            },
            name='buckley_index'),

)
