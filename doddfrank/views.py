from collections import defaultdict
from itertools import groupby
from operator import attrgetter
import datetime
import re

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.db.models import Count

from doddfrank.models import Agency, Meeting, Attendee, Organization



def index(request):
    latest_meetings = Meeting.objects.order_by('-date')[:20]
    
    agencies = Agency.objects.all()

    scope = {
        'agencies': agencies,
        'meetings': latest_meetings
    }
    return render_to_response('doddfrank/index.html', scope)


def agency_detail(request, agency_slug):
    try:
        agency = Agency.objects.get(slug=agency_slug)
    except Agency.DoesNotExist:
        raise Http404

    meetings = Meeting.objects.filter(agency=agency).order_by('-date')

    template = 'doddfrank/%s_detail.html' % agency_slug
    scope = {
        'agency': agency,
        'meetings': meetings
    }
    return render_to_response(template, scope)


def organization_disambiguation(request, organization_slug):
    organizations = Organization.objects.filter(slug=organization_slug)
    scope = {
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

    return render_to_response('doddfrank/organization_list.html',
                              {'organizations': organizations, 
                               'grouped': grouped,
                              })


def organization_frequency_table(request, agency=None):
    organizations = Organization.objects
    if agency:
        organizations = organizations.filter(agency=agency)

    organizations = organizations.annotate(num_meetings=Count('meetings')).order_by('-num_meetings')[:30]
    organizations = [org
                     for org in organizations 
                     if org.name not in [agency.name 
                                         for agency in Agency.objects.all()]]
    scope = {
        'agency': agency,
        'organizations': organizations
    }
    return render_to_response('doddfrank/organization_freq.html', scope)


def solidify_grouping(grouping):
    return dict(((k, list(vs))
                 for (k, vs) in grouping))


def meeting_detail(request, agency_slug, id):
    try:
        agency = Agency.objects.get(slug=agency_slug)
    except Agency.DoesNotExist:
        raise Http404

    try:
        meeting = Meeting.objects.get(agency=agency, pk=id)
    except Meeting.DoesNotExist:
        raise Http404

    organizations = meeting.organizations.all()
    attendees = meeting.attendees.order_by('org', 'name')
    attendee_groups = groupby(attendees, attrgetter('org'))

    template = 'doddfrank/%s_meeting_detail.html' % agency_slug
    scope = {
        'agency': agency,
        'meeting': meeting,
        'attendees': attendees,
        'attendee_groups': solidify_grouping(attendee_groups),
        'organizations': organizations,
    }
    return render_to_response(template, scope)


def search(request):
    pass

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
