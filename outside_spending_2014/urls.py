from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template, redirect_to


# 2014
urlpatterns = patterns('',
    

   url(r'^(?P<cycle>2014)/csv/race/expenditures/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),
    url(r'^(?P<cycle>2014)/csv/committees\/$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),
    url(r'^csv/committees-all-details\/$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),
    url(r'^(?P<cycle>2014)/csv/superpac-political-orientation\/$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),
    url(r'^(?P<cycle>2014)/csv/electioneering\/$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),
    url(r'^(?P<cycle>2014)/races\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/races/'}),

    url(r'^(?P<cycle>2014)/race_detail\/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/races/'}),    
    url(r'^(?P<cycle>2014)/candidates\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/house/#?candidate_filter=all'}),

    url(r'^(?P<cycle>2014)/candidate\/[\w-]+\/(?P<candidate_id>[\w\d]+)\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/house/#?candidate_filter=all'}),      
    url(r'^(?P<cycle>2014)/states\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/house/#?candidate_filter=all'}),
    url(r'^(?P<cycle>2014)/state\/(?P<state_abbreviation>\w\w)\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/house/#?candidate_filter=all'}),    
    url(r'^(?P<cycle>2014)/independent-expenditures\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/outside-spending/#?ordering=-expenditure_date_formatted'}),

    # url(r'^(?P<cycle>2014)/super-pacs/donating-organizations/', 'outside_spending_2014.views.organizational_superpac_contribs'),

    url(r'^(?P<cycle>2014)/super-pacs/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/pacs/#?ordering=-cash_on_hand&committee_class=UO'}),
    url(r'^(?P<cycle>2014)/committee\/(?P<committee_slug>[\w-]+)\/(?P<committee_id>C\d{8})\/?$', redirect_to, {'url': 'http://realtime.influenceexplorer.com/committee/%(committee_slug)s/%(committee_id)s/'}),
    url(r'^(?P<cycle>2014)/csv/committee\/(?P<committee_slug>[\w-]+)\/(?P<committee_id>C\d{8})\/?$', redirect_to, {'url': 'http://realtime.influenceexplorer.com/committee/%(committee_slug)s/%(committee_id)s/'}),
    url(r'^(?P<cycle>2014)/csv/contributions\/(?P<committee_slug>[\w-]+)\/(?P<committee_id>C\d{8})\/?$', redirect_to, {'url': 'http://realtime.influenceexplorer.com/committee/%(committee_slug)s/%(committee_id)s/'}),
    url(r'^(?P<cycle>2014)/csv/organizational-contributions\/$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),    
    url(r'^(?P<cycle>2014)/csv/all/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),    
    url(r'^(?P<cycle>2014)/csv/all/expenditures\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),    
    url(r'^(?P<cycle>2014)/csv/state/(?P<state>\w\w)\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),
    url(r'^(?P<cycle>2014)/csv/state/expenditures/(?P<state>\w\w)\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),
    url(r'^(?P<cycle>2014)/search/?$', 'outside_spending_2014.views.search'),
    url(r'^(?P<cycle>2014)/file-downloads\/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/download-index/'}),    

    url(r'^(?P<cycle>2014)/all-outside-groups/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/pacs/'}),
    url(r'^(?P<cycle>2014)/super-pacs/complete-list/?$', redirect_to, {'url':'http://realtime.influenceexplorer.com/pacs/#?ordering=-cash_on_hand&committee_class=UO'}),
)


"""
url(r'^all-outside-groups/?$', 

url(r'^super-pacs/complete-list/?$', 
url(r'^committee\/(?P<committee_slug>[\w-]+)\/(?P<committee_id>C\d{8})\/?$', 

url(r'^candidates\/?$', 
url(r'^candidate\/(?P<candidate_slug>[\w-]+)\/(?P<candidate_id>[\w\d]+)\/?$'

url(r'^states\/?$', 
url(r'^state\/(?P<state_abbreviation>\w\w)\/?$',   
url(r'^independent-expenditures\/?$', 

url(r'^super-pacs/donating-organizations/', 
url(r'^file-downloads\/?$', 
"""