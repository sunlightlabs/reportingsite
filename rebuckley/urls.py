
from django.conf.urls.defaults import *
from rebuckley.models import *
#from rebuckley.feeds import *
from rebuckley.views import *



urlpatterns = patterns('',


    url(r'^presidential\/chart\/?$', 'rebuckley.views.superpac_presidential_chart'),
    url(r'^all\/chart\/?$', 'rebuckley.views.superpac_chart'),
#    url(r'^committee\/[\w-]+\/(?P<ieonlycommittee_id>C\d{8})\/?$', 'rebuckley.views.expenditure_list'),    
    url(r'^csv/committee\/[\w-]+\/(?P<ieonlycommittee_id>C\d{8})\/?$', 'rebuckley.views.expenditure_csv'),
    url(r'^contributions\/[\w-]+\/(?P<ieonlycommittee_id>C\d{8})\/?$', 'rebuckley.views.contribs_list'),
    url(r'^csv/contributions\/[\w-]+\/(?P<ieonlycommittee_id>C\d{8})\/?$', 'rebuckley.views.contribs_csv'),    
    url(r'^csv/all/?$', 'rebuckley.views.all_contribs_csv'),    
    url(r'^csv/all/expenditures\/?$', 'rebuckley.views.all_expenditures_csv'),    
    url(r'^csv/state/(\w\w)\/?$', 'rebuckley.views.state_contribs_csv'),
    url(r'^csv/state/expenditures/(\w\w)\/?$', 'rebuckley.views.expenditure_csv_state'),
    url(r'^csv/race/expenditures/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', 'rebuckley.views.expenditure_csv_race'),
    url(r'^about/?$', 'rebuckley.views.about'),
    url(r'^all/?$', 'rebuckley.views.all_superpacs'),
    url(r'^presidential/?$', 'rebuckley.views.presidential_superpacs'),
    url(r'^president-state-detail/(?P<state>[\w0]+)\/?$', 'rebuckley.views.presidential_state_summary'),    
    url(r'^committee\/[\w-]+\/(?P<ieonlycommittee_id>C\d{8})\/?$', 'rebuckley.views.committee_detail'),          
    url(r'^races\/?$', 'rebuckley.views.races'),
    url(r'^race_detail\/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', 'rebuckley.views.race_detail'),    
    url(r'^file-downloads\/?$', 'rebuckley.views.file_downloads'),
    url(r'^candidates\/?$', 'rebuckley.views.candidates'),
    url(r'^states\/?$', 'rebuckley.views.states'),
    url(r'^state\/(?P<state_abbreviation>\w\w)\/?$', 'rebuckley.views.state_detail'),  
    url(r'^independent-expenditures\/?$', 'rebuckley.views.ies'),
    url(r'^candidate\/[\w-]+\/(?P<candidate_id>[\w\d]+)\/?$', 'rebuckley.views.candidate_detail')    
)


    
    
    
    