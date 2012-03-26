
from django.conf.urls.defaults import *
from outside_spending.models import *
#from rebuckley.feeds import *
from outside_spending.views import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',

    
    url(r'^csv/committee\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending.views.expenditure_csv'),
    url(r'^csv/contributions\/[\w-]+\/(?P<committee_id>C\d{8})\/?$', 'outside_spending.views.contribs_csv'),    
    url(r'^csv/all/?$', 'outside_spending.views.all_contribs_csv'),    
    url(r'^csv/all/expenditures\/?$', 'outside_spending.views.all_expenditures_csv'),    
    url(r'^csv/state/(\w\w)\/?$', 'outside_spending.views.state_contribs_csv'),
    url(r'^csv/state/expenditures/(\w\w)\/?$', 'outside_spending.views.expenditure_csv_state'),
    url(r'^csv/race/expenditures/(?P<office>\w)\/(?P<state>[\w0]+)\/(?P<district>\d\d)\/?$', 'outside_spending.views.expenditure_csv_race'),
    # this url used to be /super-pacs/all/ => outside-spending/super-pacs/
    url(r'^super-pacs/?$', 'outside_spending.views.all_superpacs'),
    # super-pacs/complete/  => outside-spending/super-pacs/complete-list/
    
    ### working on this one: 
    url(r'^super-pacs/complete-list/?$', 'outside_spending.views.complete_superpac_list'),
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
        
    # all that are noteworthy
    #url(r'^csv/state_csv/','outside_spending.views.states_csv'),
    #url(r'^map/',direct_to_template, {'template': 'rebuckley/map.html'}),  

)
