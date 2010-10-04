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

        if district.lower() == 'senate':
            full_race = '%s Senate' % STATE_CHOICES[state.upper()]
            office = 'S'
        else:
            try:
                if int(district) < 10:
                    district = '0%s' % district
            except ValueError:
                continue
            office = 'H'
            full_race = '%s %s' % (STATE_CHOICES[state], ordinal(district))

        # Get amounts from electioneering communications
        # where there is no race set on the expenditure.
        """
        filter = {'office': office, 'state': state, }
        if office == 'H':
            filter['district'] = district
        candidates = Candidate.objects.filter(**filter)
        already_included = [] # So we don't double count electioneering communications in the same race
        for candidate in candidates:
            expenditures = candidate.electioneering_expenditures.filter(race='')
            for expenditure in expenditures:
                if expenditure not in already_included:
                    already_included.append(expenditure)
                    if expenditure.election_type not in ('P', 'G'):
                        amounts['other'] += expenditure.expenditure_amount
                    else:
                        amounts[expenditure.election_type] += expenditure.expenditure_amount
        """

        amounts['total'] = sum([amounts['G'], amounts['P'], amounts['other']])

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
        full_race = '%s Senate' % STATE_CHOICES[state.upper()]
    else:
        if int(district) < 10:
            district = '0%s' % district
        candidates = get_list_or_404(Candidate, office='H', state=state, district=district)
        full_race = '%s %s' % (STATE_CHOICES[state.upper()], ordinal(district))

    expenditures = Expenditure.objects.filter(race=race).filter(**filter).exclude(exclude).order_by('-expenditure_date')

    # Check whether there are any electioneering
    # communications. For electioneering communications
    # that mention multiple candidates, only
    # include those where the candidates are in
    # the same race.
    electioneering = set()
    filter['race'] = ''
    for candidate in candidates:
        electioneering_communications = candidate.electioneering_expenditures.filter(**filter)
        for expenditure in electioneering_communications:
            races = set([x.race() for x in expenditure.electioneering_candidates.all()])
            if len(races) == 1:
                electioneering.add(expenditure.pk)

    expenditures = expenditures | Expenditure.objects.filter(id__in=electioneering)

    includes_electioneering = False
    if Expenditure.objects.filter(electioneering_communication=True, race=race):
        includes_electioneering = True

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
                               'includes_electioneering': includes_electioneering,
                              })

@cache_page(60*15)
def candidate_committee_detail(request, candidate_slug, committee_slug):
    if candidate_slug == 'no-candidate-listed':
        raise Http404


    committee = get_object_or_404(Committee, slug=committee_slug)

    if candidate_slug.find(',') > 0:
        candidate_slugs = candidate_slug.split(',')
        candidates = Candidate.objects.filter(slug__in=candidate_slugs)
        if not candidates:
            raise Http404

        expenditure_ids = defaultdict(int)
        for candidate in candidates:
            for e in candidate.electioneering_expenditures.all():
                expenditure_ids[e.pk] += 1
        expenditures = Expenditure.objects.filter(pk__in=[k for k, v in expenditure_ids.iteritems() if v > 1])

        candidate = None

    else:
        candidate = get_object_or_404(Candidate, slug=candidate_slug)

        expenditures = Expenditure.objects.filter(candidate=candidate,
                                                    committee=committee
                                                    ).order_by('-expenditure_date')
        candidates = [candidate,]
        # Check whether there are any electioneering
        # communications by this committee for this
        # candidate
        electioneering = candidate.electioneering_expenditures.filter(committee=committee)

        # Remove any electioneering communications
        # that also mention other candidates
        # (they'll be shown elsewhere)
        exclude = []
        for ec in electioneering:
            if ec.electioneering_candidates.count() > 1:
                exclude.append(ec.pk)

        electioneering = electioneering.exclude(pk__in=exclude)

        # Combine IEs and electioneering communications.
        expenditures = expenditures | electioneering

    if not expenditures:
        raise Http404

    return render_to_response('buckley/candidate_committee_detail.html',
                              {'object_list': expenditures, 
                               'committee': committee,
                               'candidates': candidates, 
                               'candidate_count': len(candidates),
                               'candidate': candidate,
                               'total': expenditures.aggregate(total=Sum('expenditure_amount'))['total'],
                               })

def widget():

    cache_key = 'buckley:widget2'
    dates = cache.get(cache_key)

    if not dates:
        limit = 3
        spending_list = []

        dates = Expenditure.objects.values_list('expenditure_date', flat=True).order_by('-expenditure_date').distinct()
        date_dict = defaultdict(list)
        for date in dates:

            if len(spending_list) >= limit:
                break

            expenditures = Expenditure.objects.filter(expenditure_date=date, electioneering_communication=False)

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
                        if len(spending_list) >= limit:
                            break
                        date_dict[date].append({'committee': key,
                                              'candidate': candidate,
                                              'amount': amount,
                                              'support_oppose': support_oppose,
                                              'date': date,
                                             })
                        spending_list.append(key)
                        """
                        spending_list.append({'committee': key,
                                              'candidate': candidate,
                                              'amount': amount,
                                              'support_oppose': support_oppose,
                                              'date': date,
                                             })
                        """

        dates = [(k, v) for k, v in date_dict.iteritems()]
        dates.sort(key=itemgetter(0))
        #spending_list.sort(key=itemgetter('date', 'committee', 'candidate', 'support_oppose'), reverse=True)
        cache.set(cache_key, dates, 60*60)

    return dates
    """
    return render_to_response('buckley/widget.html',
                              {'object_list': spending_list, 
                               'host': request.META['HTTP_HOST'],
                               })
    """


def embed(request):
    return render_to_response('buckley/widget.js',
            {'host': request.META['HTTP_HOST'], },
            mimetype='text/javascript')


def search(request):
    terms = request.GET.get('q', None)

    if terms:
        candidates = Candidate.objects.filter(crp_name__icontains=terms)
        committees = Committee.objects.filter(name__icontains=terms)
        num_results = candidates.count() + committees.count()
    else:
        candidates = None
        committees = None
        num_results = 0

    return render_to_response('buckley/search.html',
                              {'candidates': candidates,
                               'committees': committees,
                               'num_results': num_results,
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


def ie_stories():
    from tagging.models import TaggedItem
    from tagging.utils import get_tag
    from reporting.models import Post
    tag = get_tag('Independent Expenditures')
    posts = TaggedItem.objects.get_by_model(Post, tag)
    return posts


def multi_candidate_ecs(self, slug):
    """List electioneering communications mentioning
    the given candidate and other candidates.
    """
    candidate = get_object_or_404(Candidate, slug=slug)
    include = []
    for ec in candidate.electioneering_expenditures.all():
        if ec.electioneering_candidates.count() > 1:
            include.append(ec)

    return render_to_response('buckley/multi_candidate_ecs.html',
                             {'expenditures': include,
                              'candidate': candidate, })


def totals(request):
    ie_total = Expenditure.objects.filter(electioneering_communication=False).aggregate(total=Sum('expenditure_amount'))['total']
    ec_total = Expenditure.objects.filter(electioneering_communication=True).aggregate(total=Sum('expenditure_amount'))['total']
    total = ie_total + ec_total

    ie_only = [x.pk for x in Committee.objects.all() if x.ieonly_url()]
    ie_only_total = Expenditure.objects.filter(committee__pk__in=ie_only).aggregate(total=Sum('expenditure_amount'))['total']

    cutoff = datetime.date.today() - datetime.timedelta(days=4)

    committees = Expenditure.objects.filter(expenditure_date__gt=cutoff).order_by('committee').values('committee__name', 'committee__slug').annotate(amount=Sum('expenditure_amount')).order_by('-amount')

    return render_to_response('buckley/totals.html',
                              {'ie_total': ie_total,
                               'ec_total': ec_total,
                               'total': total,
                               'since': cutoff+datetime.timedelta(days=1),
                               'ie_only_total': ie_only_total,
                               'committees': committees, })

