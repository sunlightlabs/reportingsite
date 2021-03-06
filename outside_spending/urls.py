
from django.conf.urls.defaults import patterns, url
from outside_spending.feeds import FilingFeed, FilingsFeed, FilingsFormFeed, FilingsForms, CommitteeFormsFeed, SuperpacsForms
from django.views.generic.simple import direct_to_template, redirect_to
# 2012
urlpatterns = patterns('',

    # temporary takedown
    #url(r'^.*', direct_to_template, {'template': 'outside_spending/maintenance.html'}, name='maintenance'),
    
    url(r'^csv/committee\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending.views.expenditure_csv'),
    url(r'^csv/contributions\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending.views.contribs_csv'),
    url(r'^csv/organizational-contributions\/$', 'outside_spending.views.organizational_contribs_csv'),    
    url(r'^csv/all/?$', 'outside_spending.views.all_contribs_csv'),    
    url(r'^csv/all/expenditures\/?$', 'outside_spending.views.all_expenditures_csv'),    
    url(r'^csv/state/(\w\w)\/?$', 'outside_spending.views.state_contribs_csv'),
    url(r'^csv/state/expenditures/(\w\w)\/?$', 'outside_spending.views.expenditure_csv_state'),
    url(r'^csv/race/expenditures/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', 'outside_spending.views.expenditure_csv_race'),
    url(r'^csv/committees\/$', 'outside_spending.views.committee_summary_public'),
    url(r'^csv/committees-all-details\/$', 'outside_spending.views.committee_summary_private'),
    url(r'^csv/superpac-political-orientation\/$', 'outside_spending.views.superpac_political_orientation'),
    url(r'^csv/electioneering\/$', 'outside_spending.views.electioneering_csv'),
    # this url used to be /super-pacs/all/ => outside-spending/super-pacs/
    url(r'^super-pacs/?$', 'outside_spending.views.all_superpacs'),
    url(r'^all-outside-groups/?$', 'outside_spending.views.all_independent_expenditors'),
    # super-pacs/complete/  => outside-spending/super-pacs/complete-list/
    
    ### working on this one: 
    url(r'^super-pacs/complete-list/?$', 'outside_spending.views.complete_superpac_list'),
    url(r'^all-outside-groups/?$', 'outside_spending.views.all_independent_expenditors'), 
    # This is not used
    #url(r'^about/?$', 'outside_spending.views.about'),
    url(r'^committee\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending.views.committee_detail'),
    # super-pacs/presidential/  => outside-spending/super-pacs/presidential/
    url(r'^super-pacs/presidential/?$', 'outside_spending.views.presidential_superpacs'),
    url(r'^president-state-detail/(?P<state>[\w0]+)\/?$', 'outside_spending.views.presidential_state_summary'),
    url(r'^races\/?$', 'outside_spending.views.races'),
    url(r'^race_detail\/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', 'outside_spending.views.race_detail'),    
    url(r'^candidates\/?$', 'outside_spending.views.candidates'),
    url(r'^candidate\/[\w-]+\/(?P<candidate_id>[\w\d]+)\/?$', 'outside_spending.views.candidate_detail'),      
    url(r'^states\/?$', 'outside_spending.views.states'),
    url(r'^state\/(?P<state_abbreviation>\w\w)\/?$', 'outside_spending.views.state_detail'),    
    url(r'^independent-expenditures\/?$', 'outside_spending.views.ies'),
    # /super-pacs/contribs/organizations/ => /outside-spending/super-pacs/donating-organizations/
    url(r'^super-pacs/donating-organizations/', 'outside_spending.views.organizational_superpac_contribs'),
    url(r'^file-downloads\/?$', 'outside_spending.views.file_downloads'),    

    url(r'^electioneering-communications\/?$', 'outside_spending.views.ecs'),
    url(r'^electioneering-groups\/?$', 'outside_spending.views.all_electioneering_groups'),
    url(r'^overview\/?$', 'outside_spending.views.overview'),
    url(r'^recent-FEC-filings\/superpacs\/?$', 'outside_spending.views.recent_superpac_filings'),
    url(r'^recent-FEC-filings\/superpacs\/new-F3X\/?$', 'outside_spending.views.recent_superpac_filings_f3x'),
    url(r'^recent-FEC-filings\/independent-expenditures\/?$', 'outside_spending.views.recent_ie_filings'),    
    url(r'^recent-FEC-filings\/significant-committees\/?$', 'outside_spending.views.significant_committees'), 
    url(r'^recent-FEC-filings\/significant-committees\/new-periodic\/?$', 'outside_spending.views.significant_committees_new'), 
    #url(r'^recent-FEC-filings\/48-hr-reports\/?$', 'outside_spending.views.48hrreports'), 
    url(r'^recent-FEC-filings\/?$', 'outside_spending.views.recent_fec_filings'),
    url(r'^recent-FEC-filings\/feeds\/committee\/(?P<committee_id>C\d+)/$', FilingFeed()),    
    url(r'^recent-FEC-filings\/feeds\/committee\/(?P<committee_id>C\d+)/forms/(?P<form_types>[\w\d\-]+)/$', CommitteeFormsFeed()),
    url(r'^recent-FEC-filings\/feeds\/committees\/(?P<committee_ids>[C\d\-]+)/$', FilingsFeed()),      
    url(r'^recent-FEC-filings\/feeds\/committees\/(?P<committee_ids>[C\d\-]+)/forms/(?P<form_types>[\w\d\-]+)/$', FilingsFormFeed()),
    url(r'^recent-FEC-filings\/feeds\/forms/(?P<form_types>[\w\d\-]+)/$', FilingsForms()),
    url(r'^recent-FEC-filings\/feeds\/superpacs\/forms/(?P<form_types>[\w\d\-]+)/$', SuperpacsForms()),    
    url(r'^FEC-alerts\/$', 'outside_spending.views.recent_fec_filings_mobile'),
    url(r'^FEC-alerts\/superpacs\/?$', 'outside_spending.views.recent_fec_filings_superpacs'),
    url(r'^FEC-alerts\/superpacs\/new-F3X/?$', 'outside_spending.views.recent_fec_filings_superpacs_f3x'),
    url(r'^FEC-alerts\/independent-expenditures\/?$', 'outside_spending.views.recent_fec_filings_ies'),
    url(r'^FEC-alerts\/significant-committees\/?$', 'outside_spending.views.recent_fec_filings_significant'),
    url(r'^FEC-alerts\/significant-committees\/new-periodic\/?$', 'outside_spending.views.recent_fec_filings_significant_new'),
    url(r'^FEC-alerts\/48-hr-contrib-reports\/?$', 'outside_spending.views.recent_fec_filings_48hr_contrib'),
    url(r'^committee-search-json\/$', 'outside_spending.views.committee_search_json'),           
    url(r'^committee-search-html\/$', 'outside_spending.views.committee_search_html'), 
    url(r'^subscribe-to-alerts\/$', 'outside_spending.views.subscribe_to_alerts'), 
    url(r'^noncommittees\/$', 'outside_spending.views.noncommittees'),
    url(r'^maintenance/', direct_to_template, {'template': 'outside_spending/maintenance.html'}, name='maintenance'),
    
    url(r'^API\/candidate_summary\/(?P<candidate_id>[\w\d]+)\/?$', 'outside_spending.views.candidate_summary_json'),
    url (r'^API\/committees\/$', 'outside_spending.views.committee_summary_json'),
    
    #url(r'^searchtest\/$', 'django.views.generic.simple.direct_to_template', {'template': 'mobile_test/searchtest.html'}),      
    url(r'^search\/$', 'outside_spending.views.search'),
    url(r'^more-resources\/$', 'outside_spending.views.more_resources'),
    #url(r'^charttest\/',direct_to_template, {'template': 'outside_spending/chart_test.html', 'extra_context': {'div_name_9':'all_ies', 'div_name_1':'pres_ge_ies', 'div_name_2':'house_ge_ies', 'div_name_3':'senate_ge_ies', 'div_name_4':'all_ies_weekly', 'div_name_5':'noncommittee_affiliation', 'div_name_6':'sp_spending_partisan', 'div_name_7':'party_spending_partisan'}}, ),
    url(r'^superpac-by-party\/', redirect_to, {'url': '/outside-spending/by-affiliation/'}),
    url(r'^by-affiliation\/', 'outside_spending.views.by_affiliation'),
    url(r'^by-spending', 'outside_spending.views.by_spending'),
    url(r'^analytics\/',direct_to_template, {'template': 'outside_spending/analytical_iframe_base.html', 'extra_context': {'content':'content'}}, ),
    url(r'^superpac-chart-embed\/$', 'outside_spending.views.chart_embed'),
    #direct_to_template, {'template': 'outside_spending/chart_embedder.html', 'extra_context': {'div_name':'this_is_the_chart_div'}}, ),
    url(r'^election_summary.json$', 'outside_spending.views.elex_json'),
    url(r'^october-club\/$', 'outside_spending.views.october_club'),
    url(r'^competitive-races\/$', 'outside_spending.views.competitive_races'),
    #url(r'^new-committees\/$', 'outside_spending.views.new_committees'),
    #url(r'^new-superpacs\/$', 'outside_spending.views.new_superpacs'),
    url(r'$', 'outside_spending.views.all_superpacs'),
    

    # all that are noteworthy
    #url(r'^csv/state_csv/','outside_spending.views.states_csv'),
    #  

)

