import datetime

from django.conf.urls.defaults import *
from django.db.models import Sum
from django.views.decorators.cache import cache_page
from django.views.generic.list_detail import object_list, object_detail
from django.shortcuts import get_object_or_404

from buckley.models import *
from buckley.feeds import *
from buckley.views import *
from reporting.models import Post

about_text = ''
try:
    about_text = Post.objects.get(slug='About-page')
except Post.DoesNotExist:
    pass

KEY_PREFIX = '7'


urlpatterns = patterns('',

        # I've moved these URLS to the top and blocked the ones 
        # below with a wildcard pattern in order to take down the 
        # unlimited money tracker temporarily.
        url(r'letters\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {'queryset': IEOnlyCommittee.objects.all(), },
            name='buckley_letter_list'),

        url(r'^letters\.json$',
            'buckley.views.json_ieletter_list',
            {},
            name='buckley_json_ieletter_list'),

        url(r'letters\/rss\/?$',
            CommitteeLetterFeed(),
            name='buckley_letter_feed'),

        url(r'letters\/(?P<object_id>C\d+)\/?$',
            object_detail,
            {'queryset': IEOnlyCommittee.objects.all(), },
            name='buckley_letter_detail'),

            
        url(r'.*', 'buckley.views.redirect_to_rebuckley'),
        # This is the end of the temporary take-down block.


        url(r'^committee\/(?P<committee_slug>[-\w]+)\/(?P<object_id>\d+)\/?$',
            'buckley.views.expenditure_detail',
            {},
            name='buckley_expenditure_detail'),

        url(r'^(?P<cycle>\d{4})\/committee\/(?P<slug>[-\w]+)\/?$',
            'buckley.views.cycle_committee_detail',
            {},
            name='buckley_cycle_committee_detail'),

        url(r'^committee\/(?P<slug>[-\w]+)\/rss\/?$',
            CommitteeFeed(),
            name='buckley_committee_detail_feed'),

        url(r'^committee\/(?P<slug>[-\w]+)\/contributions\/?$',
            #'buckley.views.committee_contribution_list',
            cache_page(committee_contribution_list, 60*5, key_prefix=KEY_PREFIX),
            name='buckley_committee_contribution_list'),

        url(r'^committee\/(?P<committee_slug>[-\w]+)\/(?P<candidate_slug>[-\w]+)\/?$',
            'buckley.views.candidate_committee_detail',
            {},
            name='buckley_committee_candidate_detail'),

        url(r'^committee/(?P<slug>[-\w]+)\/?$', 
            cache_page(object_detail, 60*5, key_prefix=KEY_PREFIX),
            {'queryset': Committee.objects.all(),
             },
            name='buckley_committee_detail'),

        url(r'^(?P<cycle>\d{4})\/committee\/?$',
            'buckley.views.cycle_committee_list',
            {},
            name='buckley_cycle_committee_list'),

        url(r'^committee\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {'queryset': Committee.objects.current_cycle(), },
            name='buckley_committee_list'),

        url(r'^committee\.json\/?$',
            'buckley.views.json_committee_list',
            {},
            name='buckley_json_committee_list'),

        url(r'^committee\.csv$',
            'buckley.views.committee_list_csv',
            {},
            name='buckley_committee_list_csv'),

        url(r'^candidate\/(?P<slug>[-\w]+)\/rss\/?$',
            CandidateFeed(),
            name='buckley_candidate_detail_feed'),

        url(r'^candidate\/(?P<slug>[-\w]+)\/multi\/?$',
            'buckley.views.multi_candidate_ecs',
            {},
            name='buckley_multi_candidate_ecs'),

        url(r'^(?P<cycle>\d{4})\/candidate\/(?P<candidate_slug>[-\w\,]+)\/(?P<committee_slug>[-\w]+)\/?$',
            'buckley.views.candidate_committee_detail',
            {},
            name='buckley_cycle_candidate_committee_detail'),

        url(r'^candidate\/(?P<candidate_slug>[-\w\,]+)\/(?P<committee_slug>[-\w]+)\/?$',
            'buckley.views.candidate_committee_detail',
            {},
            name='buckley_candidate_committee_detail'),

        url(r'^(?P<cycle>\d{4})\/candidate\/(?P<slug>[-\w]+)\/?$',
            'buckley.views.cycle_candidate_detail',
            {},
            name='buckley_cycle_candidate_detail'),


        url(r'^candidate\/(?P<slug>[-\w]+)\/?$',
            cache_page(object_detail, 60*5, key_prefix=KEY_PREFIX),
            {'queryset': Candidate.objects.current_cycle(), },
            name='buckley_candidate_detail'),

        url(r'(?P<cycle>\d{4})\/candidate\/?$',
            'buckley.views.cycle_candidate_list',
            {},
            name='buckley_cycle_candidate_list'),

        url(r'candidate\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {'queryset': Candidate.objects.current_cycle(), },
            name='buckley_candidate_list'),

        url(r'candidate\.json$',
            'buckley.views.json_candidate_list',
            {},
            name='buckley_json_candidate_list'),

        url(r'candidate\.csv$',
            'buckley.views.candidate_list_csv',
            {},
            name='buckley_candidate_list_csv'),

        url(r'^race\.json$',
            'buckley.views.json_race_list',
            {},
            name='buckley_json_race_list'),

        url(r'^(?P<cycle>\d{4})\/race\/(?P<race>[-\w]+)\/?$',
            'buckley.views.race_expenditures',
            {},
            name='buckley_cycle_race_detail'),


        url(r'^race\/(?P<race>[-\w]+)\/?$',
            'buckley.views.race_expenditures',
            {},
            name='buckley_race_detail'),

        url(r'^race\/(?P<race>[-\w]+)\/rss\/?$',
            RaceFeed(),
            name='buckley_race_detail_feed'),

        url(r'race\/(?P<race>[-\w]+)\/(?P<election_type>[-\w]+)\/?$',
            'buckley.views.race_expenditures',
            {},
            name='buckley_race_election_type_detail'),

        url(r'^race\/?$',
            'buckley.views.race_list',
            {},
            name='buckley_race_list'),

        url(r'^(?P<cycle>\d{4})\/race\/?$',
            'buckley.views.race_list',
            {},
            name='buckley_cycle_race_list'),

        url(r'race\.csv$',
            'buckley.views.race_list_csv',
            {},
            name='buckley_race_list_csv'),

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

        url(r'^about\/?$',
            'django.views.generic.simple.direct_to_template',
            {'template': 'buckley/about.html', 
             'extra_context': {'about_text': about_text,
                               'latest_expenditures': Expenditure.objects.filter(expenditure_date__gte=datetime.date.today()-datetime.timedelta(days=3))[:5], 
                               'stories': ie_stories()[:5], 
                                }
            },
            name='buckley_about'),

        url(r'^stories\/?$',
                'django.views.generic.simple.direct_to_template',
                {'template': 'buckley/stories.html',
                    'extra_context': {'latest_expenditures': Expenditure.objects.filter(expenditure_date__gte=datetime.date.today()-datetime.timedelta(days=3))[:5], 
                        'stories': ie_stories(),
                        }
                    },
                name='buckley_stories'),

        url(r'^electioneering\/?$',
             cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
             {'queryset': Expenditure.objects.current_cycle(electioneering_communication=True),
                 'paginate_by': 25,
                 'template_name': 'buckley/expenditure_list.html',
                 'extra_context': {
                     'title': 'Electioneering Communications',
                     'description': 'This is spending reported to the FEC as electioneering communications.',
                     'hide_support_oppose': True,
                     'body_class': 'expendituresElectioneering',
                     'electioneering': True,
                     },
                 },
             name='buckley_electioneering_list'),

        url(r'^ie\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {'queryset': Expenditure.objects.current_cycle(electioneering_communication=False), 
             'paginate_by': 25,
             'template_name': 'buckley/expenditure_list.html',
             'extra_context': {
                 'title': 'Independent Expenditures',
                 'description': 'This is spending reported to the FEC as independent expenditures.',
                 'body_class': 'expendituresIes',
                 },
                },
            name='buckley_ie_list'),

        url(r'^(?P<cycle>\d{4})\/ie\/?$',
                'buckley.views.cycle_spending',
                {
                 'title': 'Independent Expenditures',
                 'description': 'This is spending reported to the FEC as independent expenditures.',
                 'body_class': 'expendituresIes',
                 'electioneering': False,
                 },
                name='buckley_cycle_ie_list'),

        url(r'^(?P<cycle>\d{4})\/electioneering\/?$',
                'buckley.views.cycle_spending',
                {'title': 'Electioneering Communications',
                 'description': 'This is spending reported to the FEC as electioneering communications.',
                 'hide_support_oppose': True,
                 'body_class': 'expendituresElectioneering',
                 'electioneering': True,
                },
                name='buckley_cycle_electioneering_list'),

        url(r'search\/?$',
            'buckley.views.search',
            {},
            name='buckley_search'),

        url(r'totals\/?$',
            'buckley.views.totals',
            {},
            name='buckley_totals'),

        url(r'totals\/party\/(?P<party>\w)\/(?P<support_oppose>\w)\/?$',
            'buckley.views.totals_by_party',
            {},
            name='buckley_totals_by_party'),

        url(r'aggregate_by_date\/?$',
            'buckley.views.general_aggregate_by_date',
            {},
            name='buckely_aggregate_by_date'),

        url(r'compare\/csv\/?$',
            'buckley.views.comparison_csv',
            {},
            name='buckley_comparison_csv'),

        url(r'filings\/?$',
            'buckley.views.committee_filings',
            {},
            name='buckley_committee_filings'),

        url(r'api\/committees.json$',
            'buckley.views.api_committee_list',
            {},
            name='buckley_api_committee_list'),

        url(r'api\/committees\/(?P<fec_id>C\d{8})\.json$',
            'buckley.views.api_committee_detail',
            {},
            name='buckley_api_committee_detail'),

        url(r'api\/candidates.json$',
            'buckley.views.api_candidate_list',
            {},
            name='buckley_api_candidate_list'),

        url(r'api\/candidates\/(?P<crp_id>N\d{8})\.json$',
            'buckley.views.api_candidate_detail',
            {},
            name='buckley_api_candidate_detail'),

        url(r'api\/candidates\/(?P<crp_id>N\d{8})\/?$',
                'django.views.generic.simple.direct_to_template',
                {'template': 'buckley/api_candidate_detail_table.html',
                },
                name='buckley_api_candidate_detail_table'),

        url(r'api\/candidates\/?$',
                'django.views.generic.simple.direct_to_template',
                {'template': 'buckley/api_candidate_list_table.html',
                },
                name='buckley_api_candidate_list_table'),

        url(r'api\/races.json$',
            'buckley.views.api_race_list',
            {},
            name='buckley_api_race_list'),

        url(r'api\/races\/(?P<race>[-\w]+)\.json$',
            'buckley.views.api_race_detail',
            {},
            name='buckley_api_race_detail'),

        url(r'^(?P<cycle>\d{4})\/?$',
            'buckley.views.cycle_index',
            {},
            name='buckley_cycle_index'),

        url(r'^\/?$',
            cache_page(object_list, 60*5, key_prefix=KEY_PREFIX),
            {'queryset': Expenditure.objects.current_cycle(),
             'template_name': 'buckley/index.html',
             'paginate_by': 25,
            },
            name='buckley_index'),

)
