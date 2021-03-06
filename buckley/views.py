from collections import defaultdict, deque
import csv
import datetime
from decimal import Decimal
from operator import itemgetter
import urllib2

from django.contrib.humanize.templatetags.humanize import intcomma, ordinal
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.db.models import Sum, Q
from django.db import connection
from django.http import Http404, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect

try:
    import json
except ImportError:
    import simplejson as json

STATE_CHOICES = dict(STATE_CHOICES)

from buckley.models import *
from buckley.name_tools import split as name_split

try:
    import json
except ImportError:
    import simplejson as json


KEY_PREFIX = '10'

# redirect old url to temporary new one.  
def redirect_to_rebuckley(request):
    return redirect('/super-pacs/all/')


# redirect old url to temporary new one.  
def redirect_to_superpac_listing(request):
    return redirect('/super-pacs/complete/')
        
@cache_page(60*5, key_prefix=KEY_PREFIX)
def expenditure_detail(request, committee_slug, object_id):
    expenditure = get_object_or_404(Expenditure, committee__slug=committee_slug, pk=object_id)
    return render_to_response('buckley/expenditure_detail.html', {'object': expenditure, },
                                context_instance=RequestContext(request))
                                
                                


def races(cycle=None):
    if cycle:
        candidates = Candidate.objects.filter(cycle=cycle)
        start, end = CYCLE_DATES[cycle]
        cycle_filter = {'expenditure_date__gte': start,
                        'expenditure_date__lte': end, }
    else:
        candidates = Candidate.objects.current_cycle()
        cycle_filter = {}

    races = set([x.race() for x in candidates])
    race_amts = []
    for race in races:
        try:
            state, district = race.split('-')
        except ValueError:
            continue

        amounts = Expenditure.objects.filter(race=race).filter(**cycle_filter).values('election_type').annotate(amount=Sum('expenditure_amount'))
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
            try:
                full_race = '%s %s' % (STATE_CHOICES[state], ordinal(district))
            except KeyError:
                full_race = ''

        amounts['total'] = sum([amounts['G'], amounts['P'], amounts['other']])

        race_amts.append({'race': race,
                          'full_race': full_race,
                          'amounts': amounts,
                          'total': amounts['total'], # For easier sorting
                          'cycle': cycle or '2012',
                          })

    race_amts.sort(key=itemgetter('total'), reverse=True)

    return race_amts


@cache_page(60*5, key_prefix=KEY_PREFIX)
def race_list(request, return_raw_data=False, cycle=None):
    race_amts = races(cycle)
    return render_to_response('buckley/race_list.html',
                              {'races': race_amts,
                              'cycle': cycle,
                               }, context_instance=RequestContext(request))


@cache_page(60*5, key_prefix=KEY_PREFIX)
def race_expenditures(request, race, election_type=None, cycle=None):

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
        try:
            if int(district) < 10:
                district = '0%s' % district
        except ValueError:
            raise Http404

        candidates = get_list_or_404(Candidate, office='H', state=state, district=district)
        full_race = '%s %s' % (STATE_CHOICES[state.upper()], ordinal(district))

    if cycle:
        expenditures = Expenditure.objects.all()
    else:
        expenditures = Expenditure.objects.current_cycle()

    expenditures = expenditures.filter(race=race).filter(**filter).exclude(exclude).order_by('-expenditure_date', '-pk')

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
                               'cycle': cycle,
                              }, context_instance=RequestContext(request))

@cache_page(60*5, key_prefix=KEY_PREFIX)
def candidate_committee_detail(request, candidate_slug, committee_slug, cycle=None):
    if candidate_slug == 'no-candidate-listed':
        raise Http404

    committee = get_object_or_404(Committee, slug=committee_slug)

    cycle = cycle or sorted(CYCLE_DATES.keys())[-1]

    if candidate_slug.find(',') > 0:
        candidate_slugs = candidate_slug.split(',')
        candidates = Candidate.objects.filter(slug__in=candidate_slugs, cycle=cycle)
        if not candidates:
            raise Http404

        expenditure_ids = defaultdict(int)
        for candidate in candidates:
            for e in candidate.electioneering_expenditures.all():
                expenditure_ids[e.pk] += 1
        expenditures = Expenditure.objects.filter(pk__in=[k for k, v in expenditure_ids.iteritems() if v > 1])

        candidate = None

    else:
        filter = {'slug': candidate_slug, }
        if cycle:
            filter['cycle'] = cycle
        candidate = get_object_or_404(Candidate, **filter)

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
                               'cycle': cycle,
                               }, context_instance=RequestContext(request))

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

    last_update = Expenditure.objects.order_by('-timestamp').values_list('timestamp', flat=True)
    if last_update:
        last_update = last_update[0] - datetime.timedelta(hours=4)
    else:
        last_update = None

    return dates, last_update
    """
    return render_to_response('buckley/widget.html',
                              {'object_list': spending_list, 
                               'host': request.META['HTTP_HOST'],
                               })
    """


def embed(request):
    return render_to_response('buckley/widget.js',
            {'host': request.META['HTTP_HOST'], },
            mimetype='text/javascript', 
            context_instance=RequestContext(request)
            )


def search(request):
    terms = request.GET.get('q', None)

    if terms:
        candidates = Candidate.objects.filter(crp_name__icontains=terms)
        committees = Committee.objects.filter(name__icontains=terms)
        ieonly = IEOnlyCommittee.objects.filter(name__icontains=terms)
        num_results = candidates.count() + committees.count() + ieonly.count()
      
    else:
        candidates = None
        committees = None
        num_results = 0

    return render_to_response('buckley/search.html',
                              {'candidates': candidates,
                               'committees': committees,
                               'ieonly': ieonly,
                               'num_results': num_results,
                               'terms': terms, }, context_instance=RequestContext(request))

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
    if tag:
        posts = TaggedItem.objects.get_by_model(Post, tag)
        return posts
    return Post.objects.none()


def multi_candidate_ecs(request, slug):
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
                              'candidate': candidate, }, context_instance=RequestContext(request) )


def totals(request):
    total = Total.objects.all().reverse()[0]
    top_nonparty_committees = TopCommittee.objects.order_by('-amount')[:10]
    top_party_committees = TopPartyCommittee.objects.order_by('-amount')[:10]
    top_races = TopRace.objects.order_by('-amount')[:10]
    top_candidates = TopCandidate.objects.order_by('-amount')[:10]

    pro_gop_total = total.republican_support_total + total.democrat_oppose_total
    pro_democrat_total = total.democrat_support_total + total.republican_oppose_total

    party_committee_total = total.republican_support_party + total.republican_oppose_party + total.democrat_support_party + total.democrat_oppose_party
    non_party_committee_total = total.republican_support_nonparty + total.republican_oppose_nonparty + total.democrat_support_nonparty + total.democrat_oppose_nonparty


    latest_big_expenditures = Expenditure.objects.filter(expenditure_amount__gt=250000).order_by('-expenditure_date')[:100]

    cutoff = datetime.date.today() - datetime.timedelta(days=5)

    return render_to_response('buckley/totals.html',
                              {'total': total,
                               'top_party_committees': top_party_committees,
                               'top_nonparty_committees': top_nonparty_committees,
                               'top_races': top_races,
                               'top_candidates': top_candidates,
                               'latest_big_expenditures': latest_big_expenditures, 
                               'since': cutoff+datetime.timedelta(days=1),
                               'pro_gop_total': pro_gop_total,
                               'pro_democrat_total': pro_democrat_total,
                               'party_committee_total': party_committee_total,
                               'non_party_committee_total': non_party_committee_total,
                               },
                               context_instance=RequestContext(request))


    cache_key = 'buckley:totals'
    data = cache.get(cache_key)

    if not data:
        ie_total = Expenditure.objects.filter(electioneering_communication=False).aggregate(total=Sum('expenditure_amount'))['total']
        ec_total = Expenditure.objects.filter(electioneering_communication=True).aggregate(total=Sum('expenditure_amount'))['total']
        total = ie_total + ec_total

        ie_only = [x.pk for x in Committee.objects.all() if x.ieonly_url()]
        ie_only_total = Expenditure.objects.filter(committee__pk__in=ie_only).aggregate(total=Sum('expenditure_amount'))['total']

        cutoff = datetime.date.today() - datetime.timedelta(days=4)

        committees = Expenditure.objects.filter(expenditure_date__gt=cutoff).exclude(committee__slug='').order_by('committee').values('committee__name', 'committee__slug').annotate(amount=Sum('expenditure_amount')).order_by('-amount')

        top_candidates = Expenditure.objects.filter(expenditure_date__gt=cutoff).order_by('candidate').values('candidate').annotate(amount=Sum('expenditure_amount')).order_by('-amount')[:10]
        candidates = []
        for candidate in top_candidates:
            try:
                candidate['candidate'] = Candidate.objects.get(pk=candidate['candidate'])
            except Candidate.DoesNotExist:
                continue
            candidates.append(candidate)

        top_races = Expenditure.objects.exclude(race='', candidate=None).filter(expenditure_date__gt=cutoff).order_by('race').values('race').annotate(amount=Sum('expenditure_amount')).order_by('-amount')
        races = []
        for race in top_races:
            expenditures = Expenditure.objects.filter(race=race['race'], electioneering_communication=False)
            if not expenditures:
                continue
            expenditure = expenditures[0]
            candidate = expenditure.candidate
            if not candidate:
                continue

            race['full_race_name'] = candidate.full_race_name()
            races.append(race)

        parties = {'D': 'Democrats', 'R': 'Republicans', }
        by_party = sorted(list(Expenditure.objects.exclude(support_oppose='', candidate__party='').filter(candidate__party__in=['R', 'D',]).values('candidate__party', 'support_oppose').annotate(amt=Sum('expenditure_amount'))), key=itemgetter('candidate__party', 'support_oppose'), reverse=True)
        """
        by_party += sorted(list(Expenditure.objects.exclude(support_oppose='', candidate__party__in=['R', 'D',]).values('support_oppose').annotate(amt=Sum('expenditure_amount'))), key=itemgetter('support_oppose'), reverse=True)
        for p in by_party:
            if p.has_key('candidate__party'):
                p['party'] = parties.get(p['candidate__party'])
            else:
                p['party'] = 'Others'
            #p['party'] = parties.get(p.get('candidate__party'), 'Others')
        """

        latest_big_expenditures = Expenditure.objects.filter(expenditure_amount__gt=250000).order_by('-timestamp')[:100]

        """
        states = defaultdict(Decimal)
        for race in Expenditure.objects.order_by('race').values('race').exclude(race='').annotate(amt=Sum('expenditure_amount')):
            states[race['race'].split('-')[0]] += race['amt']

        top_states = sorted(states.items, key=itemgetter(1), reverse=True)[:10]
        """
        top_states = []

        for i in by_party:
            i['party_cmtes'] = Expenditure.objects.filter(committee__tax_status='FECA Party', candidate__party=i['candidate__party'], support_oppose=i['support_oppose']).aggregate(t=Sum('expenditure_amount'))['t'] or 0
            i['non_party_cmtes'] = Expenditure.objects.exclude(committee__tax_status='FECA Party').filter(candidate__party=i['candidate__party'], support_oppose=i['support_oppose']).aggregate(t=Sum('expenditure_amount'))['t'] or 0

    data = {'ie_total': ie_total,
           'ec_total': ec_total,
           'total': total,
           'since': cutoff+datetime.timedelta(days=1),
           'ie_only_total': ie_only_total,
           'by_party': by_party,
           'latest_big_expenditures': latest_big_expenditures,
           'top_states': top_states,
           'committees': committees,
           'candidates': candidates,
           'races': races,
           }

    cache.set(cache_key, data, 60*60*24)

    return render_to_response('buckley/totals.html',
                              data,
                              context_instance=RequestContext(request))

def totals_by_party(request, party, support_oppose):
    committees = Expenditure.objects.filter(candidate__party=party, support_oppose=support_oppose).values('committee__name', 'committee__slug').annotate(t=Sum('expenditure_amount')).order_by('-t')

    party = {'R': 'Republicans',
             'I': 'Independents',
             'D': 'Democrats'}[party]

    support_oppose = {'S': 'support', 'O': 'opposition'}[support_oppose]
    print support_oppose

    return render_to_response('buckley/totals_by_party.html',
                              {'committees': committees, 
                               'party': party,
                               'support_oppose': support_oppose,
                               },
                              context_instance=RequestContext(request))



def general_aggregate_by_date(request):
    election_day = datetime.date(2010, 11, 2)
    filter = {'election_type': 'G',
              'expenditure_date__gte': election_day - datetime.timedelta(days=60)}

    data = Expenditure.objects.filter(**filter).order_by('expenditure_date').values('expenditure_date').annotate(amount=Sum('expenditure_amount'))
    dates = []
    running_total = 0
    for i in data:
        running_total += i['amount']
        dates.append((str(i['expenditure_date']), str(running_total)))

    return HttpResponse(json.dumps(dates), mimetype='application/json')


def comparison_csv(request):
    """Create a CSV comparing daily spending in 2006 
    with daily spending in 2010.
    """
    data06 = [656180, 1988810, 2002816, 2578012, 2967906, 3403189, 4456219, 8268810, 8393571, 8398721, 9194123, 11052522, 11729883, 12776705, 15420903, 15624340, 17011909, 23135004, 24392352, 27985494, 37929319, 37960392, 38058758, 41308284, 46780670, 48998314, 50777884, 66041627, 66063949, 66075226, 66908175, 74774321, 79555103, 82584861, 101912918, 102007418, 104154093, 118922522, 122280289, 124092971, 142662350, 142993616, 143055554, 148537996, 158272144, 162770505, 172912130, 195460681, 197110604, 197169484, 208893950, 215935191, 227512513, 233469664, 240413148, 240966841, 241134886, 241870247, 241956050, ]

    election_day = datetime.date(2010, 11, 2)
    cutoff = election_day - datetime.timedelta(days=60)
    data10 = []
    running_total = 0
    for i in Expenditure.objects.filter(expenditure_date__gte=cutoff).order_by('expenditure_date').values('expenditure_date').annotate(amount=Sum('expenditure_amount')):
        running_total += i['amount']
        data10.append(running_total)

    response = HttpResponse(mimetype='text/csv')
    response = HttpResponse(mimetype='text/plain')
    writer = csv.writer(response)
    writer.writerow(['Days until election', '2006', '2010', ])

    for n, i in enumerate(data06):
        days_left = 60-n
        if len(data10) > n:
            writer.writerow([n, i, data10[n], ])
        else:
            writer.writerow([n, i, 'null', ])

    return response

def comparison_chart():
    """Create a chart comparing daily spending in 2006
    with daily spending in 2010.
    """
    data06 = [656180, 1988810, 2002816, 2578012, 2967906, 
            3403189, 4456219, 8268810, 8393571, 8398721, 
            9194123, 11052522, 11729883, 12776705, 15420903, 
            15624340, 17011909, 23135004, 24392352, 27985494, 
            37929319, 37960392, 38058758, 41308284, 46780670, 
            48998314, 50777884, 66041627, 66063949, 66075226, 
            66908175, 74774321, 79555103, 82584861, 101912918, 
            102007418, 104154093, 118922522, 122280289, 124092971, 
            142662350, 142993616, 143055554, 148537996, 158272144, 
            162770505, 172912130, 195460681, 197110604, 197169484, 
            208893950, 215935191, 227512513, 233469664, 240413148, 
            240966841, 241134886, 241870247, 241956050, ]

    daily06 = [679668, 1676911, 14650, 21, 608633, 429830,
            456275, 1061030, 3863248, 124830, 5150,
            916425, 1873399, 677524, 1056169, 2644773,
            203437, 1387617, 6123095, 1257348, 3613347,
            9943827, 32335, 98366, 3252526, 5519818,
            2316090, 2029570, 15270493, 22322, 11277,
            832949, 7998082, 4794778, 3731860, 20153723,
            85300, 21181, 2583914, 14842645, 3399767,
            1812882, 18585068, 331266, 62199, 6119077,
            9736094, 4498361, 10181730, 22813488, 1650224,
            58926, 11724468, 7049546, 11577773, 5962547,
            7015403, 553693, 172502, 737545, 95310,]


    #data06 = zip([str(x) for x in range(len(data06))[::-1]], data06)
    data06 = []
    running_total = 0
    for n, i in enumerate(daily06):
        running_total += i
        data06.append((str(60-n), running_total))

    election_day = datetime.date(2010, 11, 2)
    cutoff = election_day - datetime.timedelta(days=60)

    data10 = []
    running_total = 0
    for n, i in enumerate(list(Expenditure.objects.filter(expenditure_date__gte=cutoff).order_by('expenditure_date').values('expenditure_date').annotate(amount=Sum('expenditure_amount')))):
        running_total += i['amount']
        data10.append((str(60-n), int(running_total)))

    print data06
    print data10


def committee_contribution_list(request, slug):
    committee = get_object_or_404(Committee, slug=slug)
    if not committee.has_donors:
        raise Http404

    contributions = committee.contribution_set.all()
    if not contributions:
        contributions = Contribution.objects.none()

    order_options = ('name',
                     'amount',
                     'date',
                     'occupation',
                     'employer',
                     'city',
                     'state')

    default_order = '-date'
    order = request.GET.get('order', default_order)
    if order.strip('-') not in order_options:
        order = default_order

    contributions = contributions.order_by(order)

    paginator = Paginator(contributions, 50, orphans=5)
    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        raise Http404

    return render_to_response('buckley/committee_contribution_list.html',
                              {'object_list': page.object_list,
                               'committee': committee,
                               'page_obj': page,
                               'order': order.strip('-'),
                               'sort': 'desc' if order.startswith('-') else 'asc',
                              }, context_instance=RequestContext(request))


def committee_filings(request):
    apikey = ''

    start = datetime.date.today() - datetime.timedelta(1)
    curr = start

    ids = list(CommitteeId.objects.values_list('fec_committee_id', flat=True))
    ieonly_ids = list(IEOnlyCommittee.objects.values_list('id', flat=True))
    ids = ids + ieonly_ids

    filings = []

    while True:

        if curr > datetime.date.today():
            break

        #today = datetime.date.today().strftime('%Y/%m/%d')
        date = curr.strftime('%Y/%m/%d')

        url = 'http://api.nytimes.com/svc/elections/us/v3/finances/2010/filings/%s.json?api-key=%s' % (date, apikey)

        response = urllib2.urlopen(url).read()
        data = json.loads(response)

        for result in data['results']:
            cid = re.search(r'C\d{8}', result['fec_uri']).group()
            if cid in ids and not 'HOUR' in result['report_title']:
                try:
                    committee_id = CommitteeId.objects.get(fec_committee_id=cid)
                    committee = committee_id.committee
                except CommitteeId.DoesNotExist:
                    committee = IEOnlyCommittee.objects.get(id=cid)
                result['committee_obj'] = committee
                result['date'] = curr
                filings.append(result)

        curr += datetime.timedelta(1)

    filings.sort(key=itemgetter('date'), reverse=True)

    return render_to_response('buckley/committee_filings.html',
                              {'filings': filings, 
                              }, context_instance=RequestContext(request))


def api_committee_list(request):
    committees = []
    base_url = 'http://%s%%s' % Site.objects.get_current().domain
    for committee in Committee.objects.exclude(description=''):
        if not committee.slug:
            continue
        try:
            fec_id = committee.fec_id()
        except IndexError:
            continue
        committees.append([{
            'committee': committee.name,
            'url': base_url % committee.get_absolute_url(),
            'api_url': base_url % '/independent-expenditures/api/committees/%s.json' % fec_id,
            'fec_id': committee.fec_id(),
            'total_spent': int(committee.total()),
            'independent_expenditure_total': int(committee.ie_total()),
            'electioneering_total': int(committee.ec_total()),
            'description': committee.description,
            }])
    return HttpResponse(json.dumps(committees), mimetype='text/plain')


def api_committee_detail(request, fec_id):
    committee_id = get_object_or_404(CommitteeId, fec_committee_id=fec_id)
    committee = committee_id.committee

    data = {'committee': committee.name,
            'total_spent': int(committee.total()),
            'description': committee.description, }

    base_url = 'http://%s%%s' % Site.objects.get_current().domain

    candidates = []
    candidate_list = committee.candidates_supported() | committee.candidates_opposed()
    for candidate in candidate_list:
        c = {}
        for i, j in [('S', 'supporting'), ('O', 'opposing')]:
            c[j] = Expenditure.objects.filter(committee=committee,
                                              candidate=candidate,
                                              support_oppose=i).aggregate(total=Sum('expenditure_amount')
                                                      )['total']
        candidates.append({
            'candidate': str(candidate),
            'fec_id': candidate.fec_id,
            'crp_id': candidate.crp_id,
            'party': candidate.party,
            'office': candidate.office,
            'state': candidate.state,
            'district': candidate.district if not candidate.district.startswith('S') else '',
            'race': candidate.race(),
            'url': base_url % candidate.get_absolute_url(),
            'api_url': base_url % '/independent-expenditures/api/candidates/%s.json' % candidate.crp_id,
            'total_spent': int(c['supporting'] or 0 + c['opposing'] or 0),
            'supporting': int(c['supporting'] or 0),
            'opposing': int(c['opposing'] or 0),
            })
    candidates.sort(key=itemgetter('total_spent'), reverse=True)

    data['candidates'] = candidates[:3]
    
    return HttpResponse(json.dumps(data), mimetype='text/plain')


def api_candidate_list(request):
    base_url = 'http://%s%%s' % Site.objects.get_current().domain
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM all_candidates") 

    fields = [x[0] for x in cursor.description]
    candidates = [dict(zip(fields, row)) for row in cursor.fetchall()]

    for candidate in candidates:
        del(candidate['id'])
        del(candidate['timestamp'])

        candidate['prefix'], \
                candidate['first'], \
                candidate['last'], \
                candidate['suffix'] = name_split(candidate['candidate'])

        if candidate['crp_id']:
            candidate['api_url'] = base_url % '/independent-expenditures/api/candidates/%s.json' % candidate['crp_id']
        else:
            candidate['api_url'] = ''

    return HttpResponse(json.dumps(candidates), mimetype='text/plain')


def api_candidate_detail(request, crp_id):

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM all_candidates WHERE crp_id = %s", [crp_id, ])
    candidate = dict(zip([x[0] for x in cursor.description], cursor.fetchone()))

    del(candidate['id'])
    candidate['candidate_campaign_spending'] = candidate['spending']
    del(candidate['spending'])
    del(candidate['timestamp'])

    try:
        candidate_obj = Candidate.objects.get(crp_id=candidate['crp_id'])
        candidate['outside_spending'] = int(candidate_obj.total_expenditures)
        candidate['outside_spending_supporting'] = int(candidate_obj.expenditures_supporting)
        candidate['outside_spending_opposing'] = int(candidate_obj.expenditures_opposing)
        candidate['top_outside_spending_groups'] = []
        candidate['fec_id'] = candidate_obj.fec_id
        outside_spending = sorted(candidate_obj.sole_all_committees_with_amounts(), key=itemgetter('amount'), reverse=True)
        for spending in outside_spending:
            candidate['top_outside_spending_groups'].append({
                'committee': spending['committee'].name,
                'support_oppose': spending['support_oppose'],
                'amount': int(spending['amount']),
                })
    except Candidate.DoesNotExist:
        candidate['outside_spending'] = 0
        candidate['outside_spending_supporting'] = 0
        candidate['outside_spending_opposing'] = 0
        candidate['top_outside_spending_groups'] = []

    candidate['top_contributors'] = []

    candidate['prefix'], \
            candidate['first'], \
            candidate['last'], \
            candidate['suffix'] = name_split(candidate['candidate'])


    cursor.execute("SELECT * FROM candidate_contributions WHERE candidate_crp_id = %s ORDER BY rank", [candidate['crp_id'], ])
    fields = [x[0] for x in cursor.description]
    for row in cursor.fetchall():
        data = dict(zip(fields, row))
        del(data['id'])
        del(data['candidate_crp_id'])
        del(data['timestamp'])
        candidate['top_contributors'].append(data)

    return HttpResponse(json.dumps(candidate), mimetype='text/plain')


def api_race_list(request):
    base_url = 'http://%s%%s' % Site.objects.get_current().domain
    cursor = connection.cursor()
    cursor.execute("SELECT seat, state, district, seatholder_bioguide_id FROM all_candidates WHERE use_for_sunlight_live = 1 GROUP BY seat")
    races = []
    for row in cursor.fetchall():
        data = dict(zip([x[0] for x in cursor.description], row))
        data['api_url'] = base_url % '/independent-expenditures/api/races/%(seat)s.json' % data
        if data['district'] == 'Senate':
            url = '/independent-expenditures/race/%s-Senate' % data['state']
            data['race'] = '%s Senate' % STATE_CHOICES[data['state']]
        else:
            url = '/independent-expenditures/race/%s-%s' % (data['state'], str(int(data['seat'][-2:])))
            data['race'] = '%s %s' % (STATE_CHOICES[data['state']], ordinal(data['district']))
        data['url'] = base_url % url
        races.append(data)

    return HttpResponse(json.dumps(races), mimetype='text/plain')


def api_race_detail(request, race):
    base_url = 'http://%s%%s' % Site.objects.get_current().domain
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM all_candidates WHERE seat = %s", [race, ])
    if not cursor.rowcount:
        raise Http404

    fields = [x[0] for x in cursor.description]
    candidates = [dict(zip(fields, row)) for row in cursor.fetchall()]
    seatholder_bioguide_id = candidates[0]['seatholder_bioguide_id']
    for candidate in candidates:
        del(candidate['id'])
        del(candidate['seatholder_bioguide_id'])
        candidate['candidate_campaign_spending'] = candidate['spending']
        del(candidate['spending'])
        del(candidate['timestamp'])
        del(candidate['use_for_sunlight_live'])
        try:
            candidate_obj = Candidate.objects.get(crp_id=candidate['crp_id'])
            candidate['outside_spending'] = int(candidate_obj.sole_total())
            candidate['outside_spending_supporting'] = int(candidate_obj.total_supporting())
            candidate['outside_spending_opposing'] = int(candidate_obj.total_opposing())

        except (Candidate.DoesNotExist, Candidate.MultipleObjectsReturned):
            candidate['outside_spending'] = 0
            candidate['outside_spending_supporting'] = 0
            candidate['outside_spending_opposing'] = 0

        if candidate['crp_id']:
            candidate['api_url'] = base_url % '/independent-expenditures/api/candidates/%s.json' % candidate['crp_id']
        else:
            candidate['api_url'] = ''

    race = {}
    race['candidates'] = candidates
    race['state'] = candidate['state']
    race['district'] = candidate['district']
    race['seatholder_bioguide_id'] = seatholder_bioguide_id

    if race['district'] == 'Senate':
        race['race'] = '%s Senate' % STATE_CHOICES[race['state']]
    else:
        race['race'] = '%s %s' % (STATE_CHOICES[race['state']], ordinal(race['district']))

    return HttpResponse(json.dumps(race), mimetype='text/plain')


def cycle_index(request, cycle):
    start, end = CYCLE_DATES[cycle]
    filter = {'expenditure_date__gte': start,
              'expenditure_date__lte': end, }
    expenditures = Expenditure.objects.filter(**filter)
    paginator = Paginator(expenditures, 25, orphans=5)
    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        raise Http404
    return render_to_response('buckley/index.html',
                              {'object_list': page.object_list,
                               'page_obj': page,
                               'cycle': cycle,
                               }, context_instance=RequestContext(request))


def cycle_candidate_list(request, cycle):
    candidates = get_list_or_404(Candidate, cycle=cycle)
    return render_to_response('buckley/candidate_list.html',
                              {'object_list': candidates,
                               'cycle': cycle,
                               },
                              context_instance=RequestContext(request))


def cycle_committee_list(request, cycle):
    start, end = CYCLE_DATES[cycle]
    filter = {'expenditure_date__gte': start,
              'expenditure_date__lte': end, }
    committee_ids = Expenditure.objects.filter(**filter).values_list('committee', flat=True).distinct()
    committees = Committee.objects.filter(id__in=committee_ids)
    return render_to_response('buckley/committee_list.html',
                              {'object_list': committees,
                               'cycle': cycle,
                               },
                              context_instance=RequestContext(request))


def cycle_spending(request, cycle, title, description, body_class, electioneering=False, hide_support_oppose=False):
    start, end = CYCLE_DATES[cycle]
    filter = {'expenditure_date__gte': start,
              'expenditure_date__lte': end, 
              'electioneering_communication': electioneering,
              }
    expenditures = Expenditure.objects.filter(**filter)
    paginator = Paginator(expenditures, 25, orphans=5)
    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        raise Http404
    return render_to_response('buckley/expenditure_list.html',
                                {'title': title,
                                 'description': description,
                                 'body_class': body_class,
                                 'object_list': page.object_list,
                                 'page_obj': page,
                                 'cycle': cycle,
                                 'hide_support_oppose': hide_support_oppose,
                                 'electioneering': electioneering,
                                 }, context_instance=RequestContext(request))


def cycle_candidate_detail(request, cycle, slug):
    candidate = get_object_or_404(Candidate, cycle=cycle, slug=slug)
    return render_to_response('buckley/candidate_detail.html',
                              {'object': candidate,
                               'cycle': cycle, 
                               }, context_instance=RequestContext(request))


def cycle_committee_detail(request, cycle, slug):
    committee = get_object_or_404(Committee, slug=slug)
    candidate_amounts = committee.combined_all_candidates_with_amounts(cycle)
    committee.combined_all_candidates_with_amounts = candidate_amounts
    return render_to_response('buckley/committee_detail.html',
                              {'candidate_amounts': candidate_amounts,
                               'object': committee,
                               'cycle': cycle,
                               }, context_instance=RequestContext(request))

