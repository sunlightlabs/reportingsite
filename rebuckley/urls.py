
from django.conf.urls.defaults import *
from rebuckley.models import *
#from rebuckley.feeds import *
from rebuckley.views import *



urlpatterns = patterns('',


    url(r'^presidential\/chart\/?$', 'rebuckley.views.superpac_presidential_chart'),
    url(r'^all\/chart\/?$', 'rebuckley.views.superpac_chart'),
    url(r'^committee\/[\w-]+\/(?P<ieonlycommittee_id>C\d{8})\/?$', 'rebuckley.views.expenditure_list'),    
)
    
    
    
    