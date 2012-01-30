# Create your views here.

from django.views.decorators.cache import cache_page
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response


from rebuckley.models import *


def superpac_presidential_chart(request):
    
    superpacs_with_presidential_spending = IEOnlyCommittee.objects.filter(total_presidential_indy_expenditures__gte=10)
    return render_to_response('rebuckley/superpachack_chart.html',
                              {'superpacs':superpacs_with_presidential_spending})
                              
def superpac_chart(request):

    superpacs_spending = IEOnlyCommittee.objects.filter(total_indy_expenditures__gte=10)
    return render_to_response('rebuckley/superpachack_chartall.html',
                            {'superpacs':superpacs_spending})  