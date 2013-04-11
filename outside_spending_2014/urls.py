from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template, redirect_to


# 2014
urlpatterns = patterns('',
    

    url(r'^(?P<cycle>201[24])/csv/race/expenditures/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', 'outside_spending_2014.views.expenditure_csv_race'),
    url(r'^(?P<cycle>201[24])/csv/committees\/$', 'outside_spending_2014.views.committee_summary_public'),
    url(r'^csv/committees-all-details\/$', 'outside_spending_2014.views.committee_summary_private'),
    url(r'^(?P<cycle>201[24])/csv/superpac-political-orientation\/$', 'outside_spending_2014.views.superpac_political_orientation'),
    url(r'^(?P<cycle>201[24])/csv/electioneering\/$', 'outside_spending_2014.views.electioneering_csv'),
    url(r'^(?P<cycle>201[24])/races\/?$', 'outside_spending_2014.views.races'),
    
    url(r'^(?P<cycle>201[24])/race_detail\/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', 'outside_spending_2014.views.race_detail'),    
    url(r'^(?P<cycle>201[24])/candidates\/?$', 'outside_spending_2014.views.candidates'),
    url(r'^(?P<cycle>201[24])/candidate\/[\w-]+\/(?P<candidate_id>[\w\d]+)\/?$', 'outside_spending_2014.views.candidate_detail'),      
    url(r'^(?P<cycle>201[24])/states\/?$', 'outside_spending_2014.views.states'),
    url(r'^(?P<cycle>201[24])/state\/(?P<state_abbreviation>\w\w)\/?$', 'outside_spending_2014.views.state_detail'),    
    url(r'^(?P<cycle>201[24])/independent-expenditures\/?$', 'outside_spending_2014.views.ies'),
    
    # url(r'^(?P<cycle>201[24])/super-pacs/donating-organizations/', 'outside_spending_2014.views.organizational_superpac_contribs'),
   
    url(r'^(?P<cycle>201[24])/super-pacs/?$', 'outside_spending_2014.views.all_superpacs'),
    url(r'^(?P<cycle>201[24])/committee\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending_2014.views.committee_detail'),
    url(r'^(?P<cycle>201[24])/csv/committee\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending_2014.views.expenditure_csv'),
    url(r'^(?P<cycle>201[24])/csv/contributions\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending_2014.views.contribs_csv'),
    url(r'^(?P<cycle>201[24])/csv/organizational-contributions\/$', 'outside_spending_2014.views.organizational_contribs_csv'),    
    url(r'^(?P<cycle>201[24])/csv/all/?$', 'outside_spending_2014.views.all_contribs_csv'),    
    url(r'^(?P<cycle>201[24])/csv/all/expenditures\/?$', 'outside_spending_2014.views.all_expenditures_csv'),    
    url(r'^(?P<cycle>201[24])/csv/state/(?P<state>\w\w)\/?$', 'outside_spending_2014.views.state_contribs_csv'),
    url(r'^(?P<cycle>201[24])/csv/state/expenditures/(?P<state>\w\w)\/?$', 'outside_spending_2014.views.expenditure_csv_state'),
    url(r'^(?P<cycle>201[24])/search/?$', 'outside_spending_2014.views.search'),
    url(r'^(?P<cycle>201[24])/file-downloads\/?$', 'outside_spending_2014.views.file_downloads'),    


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