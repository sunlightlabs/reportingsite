
from django.conf.urls.defaults import patterns, url
from outside_spending_2014.feeds import FilingFeed, FilingsFeed, FilingsFormFeed, FilingsForms, CommitteeFormsFeed, SuperpacsForms
from django.views.generic.simple import direct_to_template, redirect_to

urlpatterns = patterns('',

    url(r'^$', redirect_to, {'url': '/outside-spenders/2014/super-pacs/'}),

    ## redirect to 2012 b/c there are no pages for 2014 yet. 
    url(r'^super-pacs/presidential/?$', redirect_to, {'url': '/outside-spending-2012/super-pacs/presidential/'}),
    url(r'^president-state-detail/(?P<state>[\w0]+)\/?$', redirect_to, {'url': '/outside-spending-2012/president-state-detail/%(state)s/'}),
    url(r'^races\/?$', redirect_to, {'url':'/outside-spending-2012/races/'}),
    url(r'^race_detail\/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', redirect_to, {'url':'/outside-spending-2012/race_detail/%(office)s/%(state)s/%(district)s/'}),    
    url(r'^overview\/?$', redirect_to, {'url':'/outside-spending-2012/overview/'}), 
    url(r'^october-club\/$', redirect_to, {'url':'/outside-spending-2012/october-club/'}), 
    url(r'^competitive-races\/$', redirect_to, {'url':'/outside-spending-2012/competitive-races/'}), 
    url(r'^electioneering-communications\/?$', redirect_to, {'url':'/outside-spending-2012/electioneering-communications/'}),
    url(r'^electioneering-groups\/?$', redirect_to, {'url':'/outside-spending-2012/electioneering-groups/'}), 
    url(r'^super-pacs/donating-organizations/', redirect_to, {'url':'/outside-spenders/2012/super-pacs/donating-organizations/'}), 
    url(r'^superpac-by-party\/', redirect_to, {'url': '/outside-spending-2012/by-affiliation/'}),
    url(r'^by-affiliation\/', redirect_to, {'url': '/outside-spending-2012/by-affiliation/'}),
    url(r'^by-spending', redirect_to, {'url': '/outside-spending-2012/by-spending/'}),
    url(r'^analytics\/',redirect_to, {'url': '/outside-spending-2012/analytics/'}),
    url(r'^superpac-chart-embed\/$', redirect_to, {'url': 'superpac-chart-embed'}),
    
    # most people are looking for old stuff
    url(r'^candidate\/(?P<candidate_slug>[\w-]+)\/(?P<candidate_id>[\w\d]+)\/?$', redirect_to, {'url':'/outside-spending-2012/candidate/%(candidate_slug)s/%(candidate_id)s/'}),

    url(r'^super-pacs/?$', redirect_to, {'url': '/outside-spenders/2014/super-pacs/'}),
    url(r'^all-outside-groups/?$', redirect_to, {'url': '/outside-spenders/2014/all-outside-groups/'}),
    
    url(r'^super-pacs/complete-list/?$', redirect_to, {'url':'/outside-spenders/2014/super-pacs/complete-list/'}),
    url(r'^committee\/(?P<committee_slug>[\w-]+)\/(?P<committee_id>C\d{8})\/?$', redirect_to, {'url': '/outside-spenders/2014/committee/%(committee_slug)s/%(committee_id)s/'}),
    
    url(r'^candidates\/?$', redirect_to, {'url':'/outside-spenders/2014/candidates/'}),
    
    
    url(r'^states\/?$', redirect_to, {'url':'/outside-spenders/2014/states/'}),
    url(r'^state\/(?P<state_abbreviation>\w\w)\/?$', redirect_to, {'url':'/outside-spenders/2014/%(state_abbreviation)s/'}),    
    url(r'^independent-expenditures\/?$', redirect_to, {'url':'/outside-spenders/2014/independent-expenditures/'}),


    url(r'^file-downloads\/?$', redirect_to, {'url':'/outside-spenders/2014/file-downloads/'}),  

    
    ## REDIRECT TO FEC ALERTS --these shouldn't be linked anywhere, but...
    url(r'^recent-FEC-filings\/superpacs\/?$', redirect_to, {'url':'/fec-alerts/superpacs/'}),
    url(r'^recent-FEC-filings\/superpacs\/new-F3X\/?$', redirect_to, {'url':'/fec-alerts/superpacs/new-F3X\/'}),
    url(r'^recent-FEC-filings\/independent-expenditures\/?$', redirect_to, {'url':'/fec-alerts/independent-expenditures/'}),  
    url(r'^recent-FEC-filings\/significant-committees\/?$', redirect_to, {'url':'/fec-alerts/significant-committees/'}),
    url(r'^recent-FEC-filings\/significant-committees\/new-periodic\/?$',redirect_to, {'url':'/fec-alerts/significant-committees/new-periodic\/'}),
    url(r'^recent-FEC-filings\/48-hr-reports\/?$', redirect_to, {'url':'/fec-alerts/48-hr-reports/'}),
    url(r'^recent-FEC-filings\/?$', redirect_to, {'url':'/fec-alerts/'}),
    
    ## feeds -- same url, but now served from fec-alerts and powerd by 2014 data    
    url(r'^recent-FEC-filings\/feeds\/committee\/(?P<committee_id>C\d+)/$', FilingFeed()),    
    url(r'^recent-FEC-filings\/feeds\/committee\/(?P<committee_id>C\d+)/forms/(?P<form_types>[\w\d\-]+)/$', CommitteeFormsFeed()),
    url(r'^recent-FEC-filings\/feeds\/committees\/(?P<committee_ids>[C\d\-]+)/$', FilingsFeed()),      
    url(r'^recent-FEC-filings\/feeds\/committees\/(?P<committee_ids>[C\d\-]+)/forms/(?P<form_types>[\w\d\-]+)/$', FilingsFormFeed()),
    url(r'^recent-FEC-filings\/feeds\/forms/(?P<form_types>[\w\d\-]+)/$', FilingsForms()),
    url(r'^recent-FEC-filings\/feeds\/superpacs\/forms/(?P<form_types>[\w\d\-]+)/$', SuperpacsForms()),    
   
    
    url(r'^noncommittees\/$', 'outside_spending.views.noncommittees'),
    url(r'^maintenance/', direct_to_template, {'template': 'outside_spending/maintenance.html'}),
    url(r'^search\/$', 'outside_spending.views.search'),
    url(r'^more-resources\/$', 'outside_spending.views.more_resources'),


)

### CSV FILES

# url(r'^csv/committee\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending.views.expenditure_csv'),
# url(r'^csv/contributions\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending.views.contribs_csv'),
# url(r'^csv/organizational-contributions\/$', 'outside_spending.views.organizational_contribs_csv'),    
# url(r'^csv/all/?$', 'outside_spending.views.all_contribs_csv'),    
# url(r'^csv/all/expenditures\/?$', 'outside_spending.views.all_expenditures_csv'),    
# url(r'^csv/state/(\w\w)\/?$', 'outside_spending.views.state_contribs_csv'),
# url(r'^csv/state/expenditures/(\w\w)\/?$', 'outside_spending.views.expenditure_csv_state'),
# url(r'^csv/race/expenditures/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', 'outside_spending.views.expenditure_csv_race'),
# url(r'^csv/committees\/$', 'outside_spending.views.committee_summary_public'),
# url(r'^csv/committees-all-details\/$', 'outside_spending.views.committee_summary_private'),
# url(r'^csv/superpac-political-orientation\/$', 'outside_spending.views.superpac_political_orientation'),
# url(r'^csv/electioneering\/$', 'outside_spending.views.electioneering_csv'),
