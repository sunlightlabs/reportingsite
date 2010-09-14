from collections import defaultdict
from operator import itemgetter

from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.sites.models import Site
from django.http import Http404, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response

from buckley.models import *

try:
    import json
except ImportError:
    import simplejson as json


def expenditure_detail(request, committee_slug, object_id):
    expenditure = get_object_or_404(Expenditure, committee__slug=committee_slug, pk=object_id)
    return render_to_response('buckley/expenditure_detail.html', {'object': expenditure, })


def race_expenditures(request, race):
    try:
        state, district = race.split('-')
    except ValueError:
        raise Http404

    if district.lower() == 'senate':
        candidates = get_list_or_404(Candidate, office='S', state=state)
    else:
        if int(district) < 10:
            district = '0%s' % district
        candidates = get_list_or_404(Candidate, office='H', state=state, district=district)

    expenditures = Expenditure.objects.filter(candidate__in=candidates).order_by('-expenditure_date')
    total_spent = sum([x.expenditure_amount for x in expenditures])

    return render_to_response('buckley/race_detail.html',
                              {'object_list': expenditures,
                               'race': race,
                               'candidates': candidates,
                               'total_spent': total_spent,
                              })

def candidate_committee_detail(request, candidate_slug, committee_slug):
    if candidate_slug == 'no-candidate-listed':
        raise Http404
    candidate = get_object_or_404(Candidate, slug=candidate_slug)
    committee = get_object_or_404(Committee, slug=committee_slug)
    expenditures = Expenditure.objects.filter(candidate=candidate,
                                                committee=committee
                                                ).order_by('-expenditure_date')
    if not expenditures:
        return Http404

    return render_to_response('buckley/candidate_committee_detail.html',
                              {'object_list': expenditures, 
                               'committee': committee,
                               'candidate': candidate, })

def widget(request):

    max_limit = 25

    limit = request.GET.get('limit', max_limit)
    try:
        limit = int(limit)
    except ValueError:
        limit = max_limit

    if limit > max_limit:
        limit = max_limit

    spending_list = []

    dates = Expenditure.objects.values_list('expenditure_date', flat=True).order_by('-expenditure_date').distinct()
    for date in dates:
        if len(spending_list) >= limit:
            break

        expenditures = Expenditure.objects.filter(expenditure_date=date)

        pro = defaultdict(dict)
        con = defaultdict(dict)

        for expenditure in expenditures:
            if expenditure.support_oppose == 'S':
                d = pro
            elif expenditure.support_oppose == 'O':
                d = con
            else:
                continue

            if d[expenditure.committee].has_key(expenditure.candidate.slug):
                d[expenditure.committee][expenditure.candidate] += expenditure.expenditure_amount
            else:
                d[expenditure.committee][expenditure.candidate] = expenditure.expenditure_amount

        site = Site.objects.get_current()
        base_url = 'http://%s' % site.domain

        data = []
        dicts = [('support of', pro), ('opposition to', con), ]
        for support_oppose, d in dicts:
            for key, value in d.iteritems():
                for candidate, amount in value.iteritems():
                    spending_list.append({'committee': key,
                                          #'committee_url': '%s%s' % (base_url, key.get_absolute_url()),
                                          'candidate': candidate,
                                          #'candidate_url': '%s%s' % (base_url, candidate.get_absolute_url()),
                                          'amount': amount,
                                          'support_oppose': support_oppose,
                                          #'date': date.strftime('%Y-%m-%d'),
                                          'date': date,
                                         })

    spending_list.sort(key=itemgetter('date', 'committee', 'candidate', 'support_oppose'), reverse=True)

    #return HttpResponse(json.dumps(spending_list), mimetype='application/json')

    return render_to_response('buckley/widget_feed.html',
                              {'object_list': spending_list, 
                                  })
