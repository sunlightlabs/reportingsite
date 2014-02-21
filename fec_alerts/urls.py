from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',

    url(r'^$', redirect_to, {'url':'http://realtime.influenceexplorer.com/newest-filings/'}),
    url(r'^superpacs\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/newest-filings/#?ordering=-filing_number&committee_class=UO&time_range=cycle'}),
    
    url(r'^superpacs\/new-F3X\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/newest-filings/#?ordering=-filing_number&committee_class=UO&time_range=cycle&report_type=monthly'}),
    url(r'^independent-expenditures\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/newest-filings/#?ordering=-filing_number&time_range=cycle&report_type=ies'}),    
    url(r'^significant-committees\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/newest-filings/#?ordering=-filing_number&min_coh=1000000&time_range=cycle'}), 
    url(r'^significant-committees\/new-periodic\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/newest-filings/#?ordering=-filing_number&min_coh=1000000&time_range=cycle'}), 
    url(r'^48-hr-reports\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/newest-filings/#?ordering=-filing_number&time_range=cycle&report_type=F6'}), 
    #url(r'^48-hr-contrib-reports\/?$', 'fec_alerts.views.recent_fec_filings_48hr_contrib'),
    url(r'^new-committees\/$', redirect_to, {'url':'http://realtime.influenceexplorer.com/new-committees/'}),
    url(r'^new-superpacs\/$', redirect_to, {'url':'http://realtime.influenceexplorer.com/new-committees/'}),
    url(r'^subscribe-to-alerts\/$', redirect_to, {'url':'http://realtime.influenceexplorer.com/alerts/'}),
    url(r'^committee-search-html\/(?P<cycle>201[24])\/$', 'fec_alerts.views.committee_search_html'), 
    
    # url(r'^committee-search-json\/$', 'outside_spending.views.committee_search_json'),           
    # url(r'^committee-search-html\/$', 'outside_spending.views.committee_search_html'), 
    # url(r'^subscribe-to-alerts\/$', 'outside_spending.views.subscribe_to_alerts'),
    # 
    # 
    # url(r'^feeds\/committee\/(?P<committee_id>C\d+)/$', FilingFeed()),  
    # url(r'^feeds\/committee\/(?P<committee_id>C\d+)/forms/(?P<form_types>[\w\d\-]+)/$', CommitteeFormsFeed()),
    # url(r'^feeds\/committees\/(?P<committee_ids>[C\d\-]+)/$', FilingsFeed()),      
    # url(r'^feeds\/committees\/(?P<committee_ids>[C\d\-]+)/forms/(?P<form_types>[\w\d\-]+)/$', FilingsFormFeed()),
    # url(r'^feeds\/forms/(?P<form_types>[\w\d\-]+)/$', FilingsForms()),
    # url(r'^feeds\/superpacs\/forms/(?P<form_types>[\w\d\-]+)/$', SuperpacsForms()),    
    # 
)