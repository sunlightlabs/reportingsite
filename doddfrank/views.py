from collections import defaultdict
from itertools import groupby
from operator import itemgetter
import datetime
import re

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
from pymongo import Connection
from pymongo.objectid import ObjectId

def _cache_prefix():
    use_mongo = getattr(settings, 'USE_MONGO', True)
    if use_mongo:
        c = Connection()
        coll = c.test.cache_prefixes
        m = coll.find_one({'key': 'doddfrank'})
        if not m:
            return ''
        return m['prefix']
    else:
        return ''

def _collection():
    c = Connection()
    db = c.test
    return db.meetings

def _list_agencies():
    return _collection().distinct(key='agency')

def _list_organizations():
    return [x for x in sorted(list(set(sum(_collection().distinct(key='organizations'), [])))) if x]

@cache_page(60*5, key_prefix=_cache_prefix())
def index(request):
    collection = _collection()
    
    agencies = _list_agencies()
    latest_meetings = collection.find(sort=[('meeting_time', -1),])

    return render_to_response('doddfrank/index.html',
                              {'agencies': agencies,
                               'meetings': latest_meetings, }
                              )

def _organization_search(regex):
    matches = _collection().find({'organizations': {'$regex': regex, '$options': 'i'}}, fields=['organizations', ])
    organizations = [x for x in set(sum([x['organizations'] for x in matches], [])) if re.match(regex, x, re.I)]
    return organizations

def _visitor_search(regex):
    matches = _collection().find({'visitors.name': {'$regex': regex, '$options': 'i'}}, fields=['visitors.name', 'visitors.org', ])
    visitors = [x for x in set(sum([[(x['name'], x['org']) for x in m['visitors']] for m in matches], [])) if re.match(regex, x[0], re.I)]
    return visitors

def _staff_search(regex):
    cftc = _collection().find({'cftc_staff': {'$regex': regex, '$options': 'i'}}, fields=['cftc_staff', ])
    fdic = _collection().find({'agency': 'FDIC', 'staff': {'$regex': regex, '$options': 'i'}}, fields=['staff', ])

def search(request):
    q = request.GET.get('q')

    regex = '.*%s.*' % q

    re_query = {'$regex': regex, '$options': 'i'}
    fields = ['visitors.name', 
              'organizations', 
              'description', 
              'summary', 
              'staff', 
              'cftc_staff', 
              'treasury_officials',
              'participants.names', ]
    meeting_ids = []
    for field in fields:
        meeting_ids += _collection().find({field: re_query}).distinct(key='_id')

    meetings = _collection().find({'_id': {'$in': meeting_ids, }, }).sort([('meeting_time', -1)])

    return render_to_response('doddfrank/search.html',
                             {'meetings': meetings,
                              'q': q,
                             }
                             )


def _agency_lookup(agency_slug):
    """Look up an agency's full name based on its slug.
    """
    agencies = _list_agencies()
    return dict([(slugify(agency), agency) for agency in agencies]).get(agency_slug)


def _organization_lookup(organization_slug):
    """Look up an organization's full name based on its slug.
    """
    organizations = _list_organizations()
    return dict([(slugify(organization), organization) for organization in organizations]).get(organization_slug)


@cache_page(60*5, key_prefix=_cache_prefix())
def agency_detail(request, agency_slug):
    collection = _collection()
    agency = _agency_lookup(agency_slug)
    if not agency:
        raise Http404

    meetings = collection.find({'agency': agency, }, sort=[('meeting_time', -1), ])

    template = 'doddfrank/%s_detail.html' % agency_slug

    return render_to_response(template,
                              {'agency': agency,
                               'meetings': meetings, }
                              )

@cache_page(60*5, key_prefix=_cache_prefix())
def organization_detail(request, organization_slug):
    collection = _collection()
    organization = _organization_lookup(organization_slug)
    if not organization:
        raise Http404

    meetings = collection.find({'organizations': organization, }, sort=[('meeting_time', -1), ])
    return render_to_response('doddfrank/organization_detail.html',
                              {'organization': organization,
                               'meetings': meetings, }
                              )

@cache_page(60*5, key_prefix=_cache_prefix())
def organization_list(request):
    organizations = _list_organizations()

    def grouper(x):
        if not re.search(r'^[A-Za-z]', x):
            return '0-9'
        return x[0].upper()

    grouped = groupby(organizations, grouper)
    grouped = [(grouper, list(organizations)) for grouper, organizations in grouped]

    return render_to_response('doddfrank/organization_list.html',
                              {'organizations': organizations, 
                               'grouped': grouped,
                              }
                             )


@cache_page(60*5, key_prefix=_cache_prefix())
def meeting_detail(request, agency_slug, id):
    agency = _agency_lookup(agency_slug)
    if not agency:
        raise Http404

    meeting = _collection().find_one({'_id': ObjectId(id), 'agency': agency, })
    if not meeting:
        raise Http404

    template = 'doddfrank/%s_meeting_detail.html' % agency_slug

    return render_to_response(template,
                              {'agency': agency,
                               'meeting': meeting, }
                             )


def meetings_widget(request):
    cutoff = datetime.datetime.now() - datetime.timedelta(60)
    meetings = _collection().find({'meeting_time': {'$gt': cutoff}}, fields=['meeting_time', 'agency', 'organizations',]).sort([('meeting_time', -1),])
    meetings_by_date = sorted([{'date': grouper, 'meetings': list(meetings)} for grouper, meetings in groupby(meetings, lambda x: x['meeting_time'].date())], key=itemgetter('date'), reverse=True)
    return render_to_response('doddfrank/widget.html',
                              {'meetings_by_date': meetings_by_date,
                              },
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
