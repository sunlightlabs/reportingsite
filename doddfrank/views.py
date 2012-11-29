from collections import defaultdict
from itertools import groupby
from operator import attrgetter, itemgetter
from copy import copy
from StringIO import StringIO
import datetime
import re

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
from django.db.models import Q, Count, Min, Max
from django.db import connections

from doddfrank.models import Agency, Meeting, Attendee, Organization
from unicodecsv import UnicodeCsvWriter


Months = [
    (1, 'Jan', 'January'),
    (2, 'Feb', 'Febuary'),
    (3, 'Mar', 'March'),
    (4, 'Apr', 'April'),
    (5, 'May', 'May'),
    (6, 'Jun', 'June'),
    (7, 'Jul', 'July'),
    (8, 'Aug', 'August'),
    (9, 'Sep', 'September'),
    (10, 'Oct', 'October'),
    (11, 'Nov', 'November'),
    (12, 'Dec', 'December')
]


Agencies = Agency.objects.order_by('name')


def index(request):
    latest_meetings = Meeting.objects.order_by('-created', '-date')[:20]
    
    scope = {
        'agencies': Agencies,
        'meetings': latest_meetings
    }
    return render_to_response('doddfrank/index.html', scope)


def agency_detail(request, agency_slug):
    try:
        agency = Agency.objects.get(slug=agency_slug)
    except Agency.DoesNotExist:
        raise Http404

    meetings = Meeting.objects.filter(agency=agency).order_by('-date')

    template = 'doddfrank/%s_detail.html' % agency.slug
    scope = {
        'agencies': Agencies,
        'agency': agency,
        'meetings': meetings
    }
    return render_to_response(template, scope)


def organization_disambiguation(request, organization_slug):
    organizations = Organization.objects.filter(slug=organization_slug)
    scope = {
        'agencies': Agencies,
        'organizations': organizations
    }
    return render_to_response('doddfrank/organization_disambiguation.html', scope)


def organization_detail(request, organization_slug=None, organization_id=None):
    try:
        if organization_slug:
            organization = Organization.objects.get(slug=organization_slug)
        elif organization_id is not None:
            organization = Organization.objects.get(pk=organization_id)
    except Organization.DoesNotExist:
        raise Http404
    except Organization.MultipleObjectsReturned:
        return organization_disambiguation(request, organization_slug)

    scope = {
        'agencies': Agencies,
        'meetings': organization.meetings.order_by('date'),
        'organization': organization
    }
    return render_to_response('doddfrank/organization_detail.html', scope)


def organization_list(request):
    organizations = Organization.objects.order_by('name')

    def grouper(org):
        first_letter = org.name[0].upper() if org.name else ''
        if first_letter.isalpha():
            return first_letter
        else:
            return '0-9'

    grouped = groupby(organizations, grouper)
    grouped = [(grouper, list(organizations)) for grouper, organizations in grouped]

    scope = {
        'agencies': Agencies,
        'organizations': organizations, 
        'grouped': grouped,
    }
    return render_to_response('doddfrank/organization_list.html', scope)


def pivot_table(objs, rowfield, colfield, rowkeys, colkeys, valuefunc):
    if isinstance(rowfield, (str, unicode)):
        rowfield = itemgetter(rowfield)
    if isinstance(colfield, (str, unicode)):
        colfield = itemgetter(colfield)

    rows = dict.fromkeys(rowkeys, None)
    for rk in rowkeys:
        rows[rk] = {}
        for ck in colkeys:
            rows[rk][ck] = copy([])
    
    for obj in sorted(objs, key=rowfield):
        try:
            rk = rowfield(obj)
            ck = colfield(obj)
            rows[rk][ck].append(obj)
        except KeyError:
            pass

    for rk in rowkeys:
        for ck in colkeys:
            rows[rk][ck] = valuefunc(rows[rk][ck])

    return rows


def freq_table(objs, field, valuefunc):
    grouped = dict()
    for obj in objs:
        k = obj[field]
        grp = grouped.get(k, [])
        grp.append(k)
        grouped[k] = grp

    rows = [(k, valuefunc(grp)) for (k, grp) in grouped.iteritems()]
    return rows


def agency_topic_freq(request, agency_slug):
    timespan = Meeting.objects.aggregate(fro=Min('date'), to=Max('date'))
    years = range(timespan['fro'].year, timespan['to'].year + 1)

    agency = Agency.objects.get(slug=agency_slug)
    meetings = [vars(m) for m in Meeting.objects.filter(agency=agency)]
    for m in meetings:
        m['_subject'] = m['topic'] or m['subcategory'] or m['category']


    rows = freq_table(objs=meetings,
                      field='_subject',
                      valuefunc=len)

    scope = {
        'agencies': Agencies,
        'years': [str(y) for y in years],
        'agency': agency,
        'rows': sorted(rows, key=itemgetter(1), reverse=True)
    }
    return render_to_response('doddfrank/agency_topic_freq.html', scope)
               
    
def agency_topic_xtab(request, agency_slug, year):
    timespan = Meeting.objects.aggregate(fro=Min('date'), to=Max('date'))
    years = range(timespan['fro'].year, timespan['to'].year + 1)
    years = range(2010, datetime.date.today().year)

    year = int(year)
    agency = Agency.objects.get(slug=agency_slug)
    meetings = [vars(m) for m in Meeting.objects.filter(agency=agency) if m.date.year == year]
    yearmonths = set()
    subjects = set()
    for m in meetings:
        m['_subject'] = m['topic'] or m['subcategory'] or m['category']
        m['_month'] = str(m['date'].month)
        m['_year'] = str(m['date'].year)
        m['_yearmonth'] = '{_year}-{_month}'.format(**m)

        yearmonths.add(m['_yearmonth'])
        subjects.add(m['_subject'])

    colkeys = list(map(str, range(1, 13)))
    rowkeys = list(sorted(list(subjects)))

    rows = pivot_table(objs=[m for m in meetings if m['_year'] == str(year)], 
                       rowfield='_subject',
                       colfield='_month',
                       rowkeys=rowkeys,
                       colkeys=colkeys,
                       valuefunc=len)

    scope = {
        'agencies': Agencies,
        'years': years,
        'year': year,
        'agency': agency,
        'rowkeys': rowkeys,
        'colkeys': colkeys,
        'rows': rows,
        'rowlabel': 'Topic',
        'collabels': dict(((str(month), abbr) for (month, abbr, _) in Months))
    }
    return render_to_response('doddfrank/agency_topic_xtab.html', scope)


def agency_meeting_freq_table(request):
    timespan = Meeting.objects.aggregate(fro=Min('date'), to=Max('date'))
    years = range(max(2010, timespan['fro'].year),
                  min(datetime.date.today().year + 1, timespan['to'].year + 1))

    meeting_count = Meeting.objects.count()
    agencies = Agency.objects.annotate(meeting_cnt=Count('meetings'))
    meetings_per_agency_per_month = Agency.objects.extra(
        select={
            'month': 'MONTH(date)',
            'year': 'YEAR(date)'
#            'month': connections[Agency.objects.db].ops.date_trunc_sql('month', 'date'),
#            'year': connections[Agency.objects.db].ops.date_trunc_sql('year', 'date')
        },
        where=['YEAR(date) <= NOW()']).values('id', 'name', 'slug', 'year', 'month').annotate(meeting_cnt=Count('meetings'))

    # meetings is a 3-tier dict: {agency => {year => {month => meeting}}}
    meetings = {}
    for agency in agencies:
        meetings[agency.id] = {}
        for year in years:
            meetings[agency.id][year] = {}
            for (month, _abbr, _name) in Months:
                meetings[agency.id][year][month] = 0

    for agency_agg in meetings_per_agency_per_month:
        if agency_agg['year'] > datetime.date.today().year:
            continue
        meetings[agency_agg['id']][agency_agg['year']][agency_agg['month']] = agency_agg['meeting_cnt']

    per_month = {}
    per_year = {}
    for agency in agencies:
        per_year[agency.id] = {}
        per_month[agency.id] = {}
        for year in years:
            per_year[agency.id][year] = 0
            for (month, _abbr, _name) in Months:
                per_year[agency.id][year] += meetings[agency.id][year][month]
                if month not in per_month[agency.id]:
                    per_month[agency.id][month] = meetings[agency.id][year][month]
                else:
                    per_month[agency.id][month] += meetings[agency.id][year][month]

    scope = {
        'timespan': timespan,
        'years': years,
        'months': Months,
        'agencies': agencies,
        'meetings_per_agency_per_month': meetings_per_agency_per_month,
        'meeting_count': meeting_count,
        'meetings': meetings,
        'meetings_per_year': per_year,
        'meetings_per_month': per_month
    }
    return render_to_response('doddfrank/agency_meeting_freq.html', scope)
    

def organization_frequency_table(request, agency=None):
    agency_names = [a.initials for a in Agency.objects.all()]
    organizations = Organization.objects.filter(~Q(name__in=agency_names))
    if agency:
        organizations = organizations.filter(agency=agency)

    organizations = organizations.annotate(num_meetings=Count('meetings')).order_by('-num_meetings')[:30]
    organizations = [org
                     for org in organizations 
                     if org.name not in [a.name 
                                         for a in Agency.objects.all()]]
    scope = {
        'agencies': Agencies,
        'organizations': organizations
    }
    if agency:
        scope['agency'] = agency
    return render_to_response('doddfrank/organization_freq.html', scope)


def solidify_grouping(grouping):
    return dict(((k, list(vs))
                 for (k, vs) in grouping))


def meeting_detail(request, agency_slug, id):
    try:
        agency = Agency.objects.get(slug=agency_slug)
    except Agency.DoesNotExist:
        raise Http404(agency_slug)

    try:
        meeting = Meeting.objects.get(agency=agency, pk=id)
    except Meeting.DoesNotExist:
        raise Http404

    organizations = meeting.organizations.order_by('name')
    attendees = meeting.attendees.order_by('org', 'name')

    organizations = meeting.organizations.all()
    attendees = meeting.attendees.order_by('org', 'name')

    template = 'doddfrank/%s_meeting_detail.html' % agency_slug
    template = 'doddfrank/meeting_detail.html'
    scope = {
        'agencies': Agencies,
        'agency': agency,
        'meeting': meeting,
        'attendees': attendees,
        'organizations': organizations,
    }
    return render_to_response(template, scope)


def search(request, restrict_to=None):
    q = request.GET.get('q')
    scope = {
        'q': q
    }
   
    if restrict_to is None or restrict_to == 'meetings':
        do_meeting_search(q, scope,
                          limit=None if restrict_to == 'meetings' else 7)

    if restrict_to is None or restrict_to == 'attendees':
        do_attendee_search(q, scope,
                          limit=None if restrict_to == 'attendees' else 7)

    if restrict_to is None or restrict_to == 'orgs':
        do_org_search(q, scope,
                      limit=None if restrict_to == 'orgs' else 7)

    return render_to_response('doddfrank/search.html', scope)


def do_org_search(q, scope, limit=None):
    orgs = Organization.objects.filter(name__icontains=q).order_by('-id')
    scope['orgs_count'] = orgs.count()
    if limit:
        orgs = orgs[:limit]
    scope['orgs'] = orgs


def do_attendee_search(q, scope, limit=None):
    attendees = Attendee.objects.filter(name__icontains=q).order_by('-id')
    scope['attendees'] = attendees


def do_meeting_search(q, scope, limit=None):
    meetings = Meeting.objects.filter(Q(description__icontains=q)).order_by('-date')
    scope['meetings_count'] = meetings.count()
    if limit:
        meetings = meetings[:limit]
    scope['meetings'] = meetings


def meetings_widget(request):
    cutoff = datetime.datetime.now() - datetime.timedelta(60)
    meetings = Meeting.objects.filter(date__gt=cutoff).order_by('-date')

    meetings_by_date = [{'date': d, 
                         'meetings': [{'id': m.id,
                                       'topic': m.topic,
                                       'category': m.category,
                                       'subcategory': m.subcategory,
                                       'agency': m.agency,
                                       'attendees': m.attendees.all(),
                                       'organizations': m.organizations.filter(~Q(name=m.agency.name))}
                                      for m in ms]}
                        for (d, ms) in groupby(meetings, attrgetter('date'))]

    return render_to_response('doddfrank/widget.html',
                              {'meetings_by_date': meetings_by_date},
                              context_instance=RequestContext(request))


import csv
import cStringIO
import codecs

def organization_cleanup_csv(request):
    organizations = _list_organizations()
    response = HttpResponse(mimetype='text/csv')
    writer = UnicodeWriter(response)
    writer.writerow(('a', 'b'))
    for organization in organizations:
        if organization:
            writer.writerow((organization, organization))

    return response


def download_meetings(request):
    buf = StringIO()
    writer = UnicodeWriter(buf)

    writer.writerow(['agency', 'date', 'type', 'topic',
                     'attendees', 'organizations', 'source',
                     'description'])

    meetings = Meeting.objects.select_related()
    for meeting in meetings:
        writer.writerow([
            meeting.agency.initials,
            meeting.date.isoformat(),
            meeting.communication_type,
            meeting.topic or meeting.subcategory or meeting.category,
            unicode(meeting.attendees.count()),
            unicode(meeting.organizations.count()),
            meeting.source_url,
            meeting.description
        ])
    response = HttpResponse(buf.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=doddfrank_meetings.csv'
    return response


def problems(request):
    ancient_meetings = (Meeting.objects
                        .filter(date__lt=datetime.date(2010, 1, 1))
                        .order_by('-date'))
    future_meetings = (Meeting.objects
                       .filter(date__gt=datetime.date.today())
                       .order_by('-date'))

    scope = {
        'ancient_meetings': ancient_meetings,
        'future_meetings': future_meetings
    }
    return render_to_response('doddfrank/problems.html', scope)


# From http://docs.python.org/library/csv.html
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
