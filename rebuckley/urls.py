
from django.conf.urls.defaults import *
from rebuckley.models import *
#from rebuckley.feeds import *
from rebuckley.views import *



urlpatterns = patterns('',


    url(r'^chart\/?$', 'rebuckley.views.superpac_chart'),

)
    
    
    
    