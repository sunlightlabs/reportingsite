from collections import defaultdict, deque
import csv
import datetime
from operator import itemgetter

from django.views.decorators.cache import cache_page
from django.contrib.humanize.templatetags.humanize import intcomma, ordinal
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db.models import Sum, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.core.paginator import Paginator, EmptyPage, InvalidPage

try:
    import json
except ImportError:
    import simplejson as json

STATE_CHOICES = dict(STATE_CHOICES)

from buckley.models import *

try:
    import json
except ImportError:
    import simplejson as json


@cache_page(60*60)
def expenditure_detail(request, committee_slug, object_id):
    expenditure = get_object_or_404(Expenditure, committee__slug=committee_slug, pk=object_id)
    return render_to_response('buckley/expenditure_detail.html', {'object': expenditure, })


def races():
    races = set([x.race() for x in Candidate.objects.all()])
    race_amts = []
    for race in races:
        state, district = race.split('-')

        amounts = Expenditure.objects.filter(race=race).values('election_type').annotate(amount=Sum('expenditure_amount'))
        amounts = dict([(x['election_type'], x['amount']) for x in amounts])
        for k in ('P', 'G',):
            if k not in amounts:
                amounts[k] = 0
        amounts['other'] = sum([v for k, v in amounts.iteritems() if k not in ('G', 'P')])
        amounts['total'] = sum([amounts['G'], amounts['P'], amounts['other']])

        if district.lower() == 'senate':
            full_race = '%s Senate' % STATE_CHOICES[state]
        else:
            try:
                if int(district) < 10:
                    district = '0%s' % district
            except ValueError:
                continue
            full_race = '%s %s' % (STATE_CHOICES[state], ordinal(district))

        race_amts.append({'race': race,
                          'full_race': full_race,
                          'amounts': amounts,
                          'total': amounts['total'], # For easier sorting
                          })

    race_amts.sort(key=itemgetter('total'), reverse=True)

    return race_amts


@cache_page(60*15)
def race_list(request, return_raw_data=False):
    race_amts = races()
    return render_to_response('buckley/race_list.html',
                              {'races': race_amts,
                               })


@cache_page(60*15)
def race_expenditures(request, race, election_type=None):

    try:
        state, district = race.split('-')
    except ValueError:
        raise Http404

    filter = {}
    exclude = Q()
    election_types = {'primary': 'P', 'general': 'G', }
    if election_type:
        if election_type in election_types:
            filter = {'election_type': election_types[election_type]}
        else:
            exclude = Q(election_type='G') | Q(election_type='P')

    if district.lower() == 'senate':
        candidates = get_list_or_404(Candidate, office='S', state=state)
        full_race = '%s Senate' % STATE_CHOICES[state]
    else:
        if int(district) < 10:
            district = '0%s' % district
        candidates = get_list_or_404(Candidate, office='H', state=state, district=district)
        full_race = '%s %s' % (STATE_CHOICES[state], ordinal(district))

    expenditures = Expenditure.objects.filter(race=race).filter(**filter).exclude(exclude).order_by('-expenditure_date')
    if not expenditures:
        raise Http404

    election_types = []
    if not election_type:
        types = deque(expenditures.order_by('election_type').values_list('election_type', flat=True).distinct())
        if 'G' in types:
            election_types.append({'election_type': 'General', 'slug': 'general'})
            types.remove('G')
        if 'P' in types:
            election_types.append({'election_type': 'Primary', 'slug': 'primary'})
            types.remove('P')
        if types:
            election_types.append({'election_type': 'Other', 'slug': 'other'})

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
                               'short_race': race,
                               'candidates': candidates,
                               'total_spent': total_spent,
                               'page_obj': page,
                               'election_types': election_types,
                               'election_type': election_type,
                              })

@cache_page(60*15)
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

    cache_key = 'buckley:widget'
    spending_list = cache.get(cache_key)

    if not spending_list:
        limit = 25
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
        cache.set(cache_key, spending_list, 60*60)

    return render_to_response('buckley/widget.html',
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

def committee_list_csv(request):
    fields = ['ID', 'Committee', 'Total spent on independent expenditures', 'As of', ]
    rows = []
    for committee in Committee.objects.order_by('name'):
        rows.append([committee.fec_id(), committee.name, committee.total(), datetime.date.today(), ])
    return generic_csv('committee.csv', fields, rows)

def candidate_list_csv(request):
    fields = ['ID', 'Candidate', 'Party', 'Office', 'State', 'Total independent expenditures', 'Total independent expenditures supporting', 'Total independent expenditures opposing', 'As of', ]
    rows = []
    for candidate in Candidate.objects.order_by('fec_name'):
        rows.append([candidate.fec_id, candidate.last_first(), candidate.party, candidate.office, candidate.state, candidate.total(), candidate.total_supporting(), candidate.total_opposing(), datetime.date.today(), ])
    return generic_csv('candidate.csv', fields, rows)

def race_list_csv(request):
    fields = ['Office', 'State', 'General election independent expenditures', 'Primary election independent expenditures', 'Other election independent expenditures', 'Total independent expenditures', 'As of', ]
    rows = []
    #races = races() #race_list(request, True)
    for race in races():
        state, district = race['race'].split('-')
        if district == 'Senate':
            office = 'S'
        else:
            office = 'H'
        rows.append([office, state, race['amounts']['G'], race['amounts']['P'], race['amounts']['other'], race['amounts']['total'], datetime.date.today()])

    return generic_csv('race.csv', fields, rows)


def generic_csv(filename, fields, rows):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    writer = csv.writer(response)
    writer.writerow(fields)
    for row in rows:
        writer.writerow(row)

    return response


def json_committee_list(request):
    committees = []
    for committee in Committee.objects.order_by('name'):
        committees.append(['<a href="%s">%s</a>' % (committee.get_absolute_url(), committee.name),
                           intcomma(committee.total()),
                           '<a href="http://query.nictusa.com/cgi-bin/fecimg/?%s">FEC Filings</a>' % committee.fec_id(), ])
    headers = ['Committee', 'Total spent on independent expenditures', '', ]
    data = {'headers': headers, 'data': committees, }
    return HttpResponse(json.dumps(data), mimetype='application/json')


def json_candidate_list(request):
    candidates = []
    for candidate in Candidate.objects.order_by('fec_name'):
        candidates.append(['<a href="%s">%s</a>' % (candidate.get_absolute_url(), candidate.last_first()),
                           candidate.party,
                           candidate.full_race_name(),
                           intcomma(candidate.total()),
                           intcomma(candidate.total_supporting()),
                           intcomma(candidate.total_opposing()), ])
    headers = ['Candidate', 'Party', 'Race', 
                'Total independent expenditures',
                'Independent expenditures supporting',
                'Independent expenditures opposing', ]
    data = {'headers': headers, 'data': candidates, }
    return HttpResponse(json.dumps(data), mimetype='application/json')


def json_race_list(request):
    race_list = []
    for race in races():
        race_list.append([race['full_race'],
                        intcomma(race['amounts']['G']),
                        intcomma(race['amounts']['P']),
                        intcomma(race['amounts']['other']),
                        intcomma(race['total']), ])
    headers = ['Race', 'General', 'Primary', 'Other', 'Total', ]
    data = {'headers': headers, 'data': race_list, }
    return HttpResponse(json.dumps(data), mimetype='application/json')


def json_ieletter_list(request):
    committees = []
    for committee in IEOnlyCommittee.objects.all():
        if committee.has_expenditures():
            expenditures_link = '<a href="%s">View expenditures</a>' % committee.has_expenditures().get_absolute_url()
        else:
            expenditures_link = 'No expenditures reported'
        committees.append(['<a href="%s">%s</a>' % (committee.get_absolute_url(),
                                                    committee.name),
                           committee.date_letter_submitted.strftime('%m/%d/%y'),
                           expenditures_link,
                           '<a href="http://images.nictusa.com/cgi-bin/fecimg/?%s" target="new">View all FEC filings</a>' % (committee.pk),
                           ])
    headers = ['Committee', 'Date letter filed', '', '', ]
    data = {'headers': headers, 'data': committees, }
    return HttpResponse(json.dumps(data), mimetype='application/json')

