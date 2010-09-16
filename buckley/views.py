from collections import defaultdict
from operator import itemgetter

from django.contrib.humanize.templatetags.humanize import intcomma, ordinal
from django.contrib.sites.models import Site
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.core.paginator import Paginator, EmptyPage, InvalidPage

STATE_CHOICES = dict(STATE_CHOICES)

from buckley.models import *

try:
    import json
except ImportError:
    import simplejson as json


def expenditure_detail(request, committee_slug, object_id):
    expenditure = get_object_or_404(Expenditure, committee__slug=committee_slug, pk=object_id)
    return render_to_response('buckley/expenditure_detail.html', {'object': expenditure, })


def race_list(request):

    order = request.GET.get('order', 'amt')
    direction = request.GET.get('sort', None)
    if order != 'amt' and not direction:
        direction = 'asc'
    elif order == 'amt' and not direction:
        direction = 'desc'

    races = set([x.race() for x in Candidate.objects.all()])
    race_amts = []
    for race in races:
        state, district = race.split('-')
        if district.lower() == 'senate':
            total = sum([x.total() for x in Candidate.objects.filter(office='S', state=state)])
            full_race = '%s Senate' % STATE_CHOICES[state]
        else:
            try:
                if int(district) < 10:
                    district = '0%s' % district
            except ValueError:
                continue
            full_race = '%s %s' % (STATE_CHOICES[state], ordinal(district))
            total = sum([x.total() for x in Candidate.objects.filter(office='H', state=state, district=district)])
        race_amts.append((race, full_race, total))

    rev = direction == 'desc'
    sort_item = 2 if order == 'amt' else 1

    race_amts.sort(key=itemgetter(sort_item), reverse=rev)

    return render_to_response('buckley/race_list.html',
                              {'races': race_amts,
                               'sort': 'asc' if direction == 'desc' else 'desc'
                               })


def race_expenditures(request, race):
    try:
        state, district = race.split('-')
    except ValueError:
        raise Http404

    if district.lower() == 'senate':
        candidates = get_list_or_404(Candidate, office='S', state=state)
        full_race = '%s Senate' % STATE_CHOICES[state]
    else:
        if int(district) < 10:
            district = '0%s' % district
        candidates = get_list_or_404(Candidate, office='H', state=state, district=district)
        full_race = '%s %s' % (STATE_CHOICES[state], ordinal(district))

    #expenditures = Expenditure.objects.filter(candidate__in=candidates).order_by('-expenditure_date')
    expenditures = Expenditure.objects.filter(race=race).order_by('-expenditure_date')
    if not expenditures:
        raise Http404

    paginator = Paginator(expenditures, 50, orphans=5)
    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        raise Http404

    #total_spent = sum([x.expenditure_amount for x in expenditures])
    total_spent = expenditures.aggregate(total=Sum('expenditure_amount'))['total']

    return render_to_response('buckley/race_detail.html',
                              {'object_list': page.object_list,
                               'race': full_race,
                               'candidates': candidates,
                               'total_spent': total_spent,
                               'page_obj': page,
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

            if d[expenditure.committee].has_key(expenditure.candidate):
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
                                          'candidate': candidate,
                                          'amount': amount,
                                          'support_oppose': support_oppose,
                                          'date': date,
                                         })

    spending_list.sort(key=itemgetter('date', 'committee', 'candidate', 'support_oppose'), reverse=True)

    #return HttpResponse(json.dumps(spending_list), mimetype='application/json')

    return render_to_response('buckley/widget_feed.html',
                              {'object_list': spending_list, 
                               'host': request.META['HTTP_HOST'],
                                  })


def embed(request):
    return render_to_response('buckley/widget.js',
            {'host': request.META['HTTP_HOST'], },
            mimetype='text/javascript')


def search(request):
    terms = request.GET.get('q', None)

    if terms:
        candidates = Candidate.objects.filter(crp_name__icontains=terms)
        committees = Committee.objects.filter(name__icontains=terms)
    else:
        candidates = None
        committees = None

    return render_to_response('buckley/search.html',
                              {'candidates': candidates,
                               'committees': committees,
                               'num_results': candidates.count() + committees.count(),
                               'terms': terms, })
