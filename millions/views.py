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
    from django.db.models import Q
    filterparams = ['awarding_agency_name', 'award_type', 'pop_state_cd', 'recipient_state', 'project_activity_desc' ]
    selectedf = []
    for p in filterparams:
        selectedf.append([p, None]) 
    selectedfilters = dict(selectedf)
    if request.GET:
        for p in filterparams:
            if p in request.GET:
                selectedfilters[p] = request.GET[p]

    baseqs = Record.objects.filter(version_flag='F').exclude(status='x')
    qs = baseqs

    award_key = ''
    if 'award_key' in request.GET:
        award_key = request.GET['award_key']
        qs = qs.filter(award_key=award_key)
        return render_to_response('millions/table.html', {"recs":qs, "selectedfilters": selectedfilters, 'filterparams': filterparams, 'award_key': award_key }, context_instance=RequestContext(request))

      
    if selectedfilters['award_type']:
        qs = qs.filter(award_type=selectedfilters['award_type'][:1])
    if selectedfilters['awarding_agency_name']:
        qs = qs.filter(awarding_agency_name=selectedfilters['awarding_agency_name'])
    if selectedfilters['pop_state_cd']:
        qs = qs.filter(pop_state_cd=selectedfilters['pop_state_cd'])
    if selectedfilters['project_activity_desc']:
        qs = qs.filter(project_activity_desc=selectedfilters['project_activity_desc'])
    primes = qs.filter(recipient_role='P').values_list('award_key')

    myQ = Q()
    for prime in primes:
        myQ = myQ | Q(award_key=prime[0])
    
    allqs = baseqs.filter(myQ)

    return render_to_response('millions/table.html', {"recs":allqs, 'primes': primes, "selectedfilters": selectedfilters, 'filterparams': filterparams, 'award_key': award_key }, context_instance=RequestContext(request))


def tree(request):
    import datetime

    sumon = ['award_amount', 'total_fed_arra_exp', 'number_of_jobs']
    sumonselected = 'award_amount'
    xyorder=[]
    filterparams = ['awarding_agency_name', 'award_type', 'pop_state_cd', 'project_activity_desc', 'recipient_state', 'recipient_namee' ]
    selectedf = []
    xychoices = ['award_type', 'awarding_agency_name', 'pop_state_cd', 'project_activity_desc',  ]
    xyfinal = ['recipient_namee', 'project_description']
    for p in filterparams:
        selectedf.append([p, None]) 
    selectedfilters = dict(selectedf)
    if request.GET:
        if 'sumon' in request.GET and request.GET['sumon']:
            sumonselected = request.GET['sumon']
        for p in filterparams:
            if p in request.GET and request.GET[p]:
                selectedfilters[p] = request.GET[p]
        if 'sliceby' in request.GET and request.GET['sliceby']:        
            sliceby = request.GET['sliceby'].split(',')
            for x in sliceby:
                if int(x)<len(xychoices):            
                    xyorder.append( xychoices[int(x)] )
    if len(xyorder)==0:
        xyorder = xychoices
    xyused = []
    for x in xyorder:
        if x not in selectedfilters or not selectedfilters[x]:
            xyused.append(x)
    if len(xyused)<2:
        for x in xyfinal:
            xyused.append(x)
    
    qs = Record.objects.filter(version_flag='F').exclude(status='x')
    if sumonselected=='number_of_jobs':
        qs = qs.filter(fiscal_qtr=4)
    else:
        qs = qs.filter(recipient_role='P')
    if selectedfilters['award_type']:
        qs = qs.filter(award_type=selectedfilters['award_type'][:1])
    if selectedfilters['awarding_agency_name']:
        qs = qs.filter(awarding_agency_name=selectedfilters['awarding_agency_name'])
    if selectedfilters['pop_state_cd']:
        qs = qs.filter(pop_state_cd=selectedfilters['pop_state_cd'])
    if selectedfilters['project_activity_desc']:
        qs = qs.filter(project_activity_desc=selectedfilters['project_activity_desc'])
    if selectedfilters['recipient_namee']:
        qs = qs.filter(recipient_namee=selectedfilters['recipient_namee'])

    if len(xyused)==0:
        return detail(request)
    if len(xyused)==1:
        records = qs.values(xyused[0]).annotate(Sum(sumonselected)).values_list(sumonselected+'__sum', xyused[0])
    if len(xyused)>=2:
        records = qs.values(xyused[0], xyused[1]).annotate(Sum(sumonselected)).values_list(sumonselected+'__sum', xyused[0], xyused[1])

 
    return render_to_response('millions/tree.html', {"recs":records, "selectedfilters": selectedfilters, 'filterparams': filterparams, 'xy': xyorder, 'sumon': sumon, 'sumonselected': sumonselected, 'xyused': xyused, 'xyfinal': xyfinal, 'xychoices': xychoices }, context_instance=RequestContext(request))





def reciptree(request):
    if request.GET:
        if 'name' in request.GET:
            recipient_namee = request.GET['name']
    sub = []
    qs = Record.objects.filter(version_flag='F', recipient_role='P', recipient_namee=recipient_namee).exclude(status='x')
    for q in qs:
        if q.project_name:
            awardtext = q.project_name
        else:
            awardtext = q.project_description
        qsc = Record.objects.filter(version_flag='F').filter(award_key=q.award_key).exclude(status='x',recipient_role='P')
        for c in qsc:
            sub.append( [ c.local_amount, awardtext, c.recipient_namee, q.award_key ] )
        sub.append( [ q.local_amount, awardtext, '(prime)', q.award_key ] )

                         

       
    return render_to_response('millions/tree2.html', {"recs":sub, 'recipient': recipient_namee }, context_instance=RequestContext(request))
