from collections import defaultdict
import re

from pymongo import Connection
from pymongo.objectid import ObjectId

from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.http import Http404, HttpResponse


def _collection():
    c = Connection()
    db = c.test
    return db.meetings

def _list_agencies():
    return _collection().distinct(key='agency')

def _list_organizations():
    return sorted(list(set(sum(_collection().distinct(key='organizations'), []))))

def index(request):
    collection = _collection()
    
    agencies = _list_agencies()
    latest_meetings = collection.find(sort=[('meeting_time', -1),])

    return render_to_response('doddfrank/index.html',
                              {'agencies': agencies,
                               'meetings': latest_meetings, }
                              )


def search(request):
    q = request.GET.get('q')

    regex = '.*%s.*' % q
    meeting_ids = []
    meeting_ids +=  _collection().find({'visitors.name': {'$regex': regex, '$options': 'i'}}).distinct(key='_id')
    meeting_ids += _collection().find({'organizations': {'$regex': regex, '$options': 'i'}}).distinct(key='_id')

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

def organization_list(request):
    organizations = _list_organizations()
    return render_to_response('doddfrank/organization_list.html',
                              {'organizations': organizations, 
                              }
                             )


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