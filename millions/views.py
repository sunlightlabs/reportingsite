from django.conf import settings
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from millions.models import *
import random
import simplejson
import time
import datetime
from django.template import RequestContext

from django.db.models.query import QuerySet

from django.db.models import *
#
# view methods
#



def detail(request):
    filterparams = ['awarding_agency_name', 'award_type', 'pop_state_cd' ]
    selectedf = []
    for p in filterparams:
        selectedf.append([p, None]) 
    selectedfilters = dict(selectedf)
    if request.GET:
        for p in filterparams:
            if p in request.GET:
                selectedfilters[p] = request.GET[p]
      
    qs = Record.objects.all()
    if selectedfilters['award_type']:
        qs = qs.filter(award_type=selectedfilters['award_type'])
    if selectedfilters['awarding_agency_name']:
        qs = qs.filter(awarding_agency_name=selectedfilters['awarding_agency_name'])
    if selectedfilters['pop_state_cd']:
        qs = qs.filter(pop_state_cd=selectedfilters['pop_state_cd'])
    return render_to_response('millions/table.html', {"recs":qs, "selectedfilters": selectedfilters, 'filterparams': filterparams}, context_instance=RequestContext(request))


def tree(request):
    sumon = ['award_amount', 'total_fed_arra_exp', 'number_of_jobs']
    sumonselected = 'award_amount'
    selectedxy=None
    filterparams = ['awarding_agency_name', 'award_type', 'pop_state_cd' ]
    selectedf = []
    xychoices = ['award_type', 'awarding_agency_name', 'recipient_state', 'project_activity_desc']
    xy = ['award_type', 'awarding_agency_name']
    for p in filterparams:
        selectedf.append([p, None]) 
    selectedfilters = dict(selectedf)
    if request.GET:
        for p in filterparams:
            if p in request.GET:
                selectedfilters[p] = request.GET[p]
        if 'sliceby' in request.GET:        
            selectedxy = request.GET['sliceby'].split(',')
        xy = []
        for x in selectedxy:
            xy.append(xychoices[int(x)])
        sumonselected = request.GET['sumon']

    qs = Record.objects.all()
    if sumonselected!='number_of_jobs':
        qs = qs.filter(recipient_role__startswith='P')
    if selectedfilters['award_type']:
        qs = qs.filter(award_type=selectedfilters['award_type'])
    if selectedfilters['awarding_agency_name']:
        qs = qs.filter(awarding_agency_name=selectedfilters['awarding_agency_name'])
    if selectedfilters['pop_state_cd']:
        qs = qs.filter(pop_state_cd=selectedfilters['pop_state_cd'])
    #if selectedfilters['project_activity_desc']:
    #    qs = qs.filter(project_activity_desc=selectedfilters['project_activity_desc'])


    if len(xy)==1:
        records = qs.values(xy[0]).annotate(Sum(sumonselected)).values_list(sumonselected+'__sum', xy[0])
    if len(xy)==2:
        records = qs.values(xy[0], xy[1]).annotate(Sum(sumonselected)).values_list(sumonselected+'__sum', xy[0], xy[1])
    if len(xy)>2:
        records = qs.values(xy[0], xy[1], xy[2]).annotate(Sum(sumonselected)).values_list(sumonselected+'__sum', xy[0], xy[1], xy[2])


 
    return render_to_response('millions/tree.html', {"recs":records, "selectedfilters": selectedfilters, 'filterparams': filterparams, 'xy': xy, 'xychoices': xychoices, 'slicebyvals': selectedxy, 'sumon': sumon, 'sumonselected': sumonselected }, context_instance=RequestContext(request))
