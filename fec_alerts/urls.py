from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',

    url(r'^$', 'fec_alerts.views.recent_fec_filings'),
    url(r'^superpacs\/?$', 'fec_alerts.views.recent_superpac_filings'),
    url(r'^superpacs\/new-F3X\/?$', 'fec_alerts.views.recent_superpac_filings_f3x'),
    url(r'^independent-expenditures\/?$', 'fec_alerts.views.recent_ie_filings'),    
    url(r'^significant-committees\/?$', 'fec_alerts.views.significant_committees'), 
    url(r'^significant-committees\/new-periodic\/?$', 'fec_alerts.views.significant_committees_new'), 
    url(r'^48-hr-reports\/?$', 'fec_alerts.views.recent_fec_filings_48hr_contrib'), 
    url(r'^significant-committees\/?$', 'fec_alerts.views.recent_fec_filings_significant'),
    url(r'^significant-committees\/new-periodic\/?$', 'fec_alerts.views.recent_fec_filings_significant_new'),
    #url(r'^48-hr-contrib-reports\/?$', 'fec_alerts.views.recent_fec_filings_48hr_contrib'),
    url(r'^new-committees\/$', 'fec_alerts.views.new_committees'),
    url(r'^new-superpacs\/$', 'fec_alerts.views.new_superpacs'),
    url(r'^subscribe-to-alerts\/$', 'fec_alerts.views.subscribe_to_alerts'),
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