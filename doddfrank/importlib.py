import sys
import hashlib
import json

import requests
import progressbar
import dateutil.parser

from django.db.models import Count

from doddfrank.models import Agency, Meeting, Attendee


def agency_or_die(initials):
    try:
        return Agency.objects.get(initials=initials)
    except Agency.DoesNotExist:
        print >>sys.stderr, '{0} is not a registered agency.'.format(initials)
        sys.exit(1)


def slurp_data(url):
    response = requests.get(url)
    assert response.status_code == 200, 'Unable to fetch {0}'.format(url)
    data = json.loads(response.content)
    if isinstance(data, list):
        """ This is the success condition. """
        return data

    error = (data.get('error')
             if hasattr(data, 'get')
             else 'Data returned from ScraperWiki was not a list of objects: {0}'.format(data))
    assert isinstance(data, list), error
    

def dict_hash(d, hashfunc=hashlib.md5):
    if isinstance(d, dict) == False:
        import ipdb; ipdb.set_trace()

    d_hash = hashfunc()
    for (k, v) in sorted(d.items()):
        d_hash.update(k.encode('utf-8', 'replace'))
        if v:
            d_hash.update(v.encode('utf-8', 'replace'))
    return d_hash.hexdigest()


class DictSlicer(object):
    def __init__(self, *ks):
        self.ks = ks

    def __call__(self, d):
        return dict(((k, v) for (k, v) in d.iteritems() if k in self.ks))


def index_dict_list(l, keys):
    slicer = DictSlicer(*keys)
    return dict(((dict_hash(slicer(d)), d)
                 for d in l))


def reconcile_database(objects, records):
    """
    Determines which database objects are no longer in the
    CSV records and thus candidates for deletion.
    """

    print 'Reconciling all database objects.'

    duplicated = []
    deprecated = []

    progress = progressbar.ProgressBar(maxval=objects.count())

    for obj in progress(objects):
        matches = [(rec, obj)
                   for rec in records
                   if dict_hash(rec) == obj.import_hash]

        if len(matches) == 0:
            deprecated.append(obj)
        elif len(matches) > 1:
            duplicated.extend(matches)

    if len(deprecated) > 0:
        print 'Deleting meetings no longer in CSV records:'
        for obj in deprecated:
            print repr(obj)
            obj.delete()

    if len(duplicated) > 0:
        print 'Meetings seemingly duplicated:'
        for (rec, obj) in duplicated:
            print repr(obj)


def import_meetings(meetings, keyfunc, copyfunc):
    """
    meetings is a list of objects pulled from ScraperWiki

    keyfunc is a function of a record and the hash of that record.
    It should return a dictionary suitable for selecting a unique
    database record.

    copyfunc is a function of a record and a Meeting object. It
    should copy fields from the record to the appropriate fields
    of the database object.
    """

    progress = progressbar.ProgressBar()
    for m in progress(meetings):
        m_hash = dict_hash(m)
        keys = keyfunc(m, m_hash)
        (meeting, created) = Meeting.objects.get_or_create(**keys)
        if created:
            copyfunc(m, meeting)
            meeting.import_hash = m_hash
            meeting.save()


def prune_attendees():
    """
    If a Meeting is dropped we cannot drop all of the associated
    Attendee objects because they may be associated with another
    meeting. Thus we must take care to eliminate Attendee objects
    that are no longer associated with any Meeting objects.

    Most of these orphaned Attendee objects are the result of changes
    to the name parsing logic.
    """
    attendees_to_drop = Attendee.objects.annotate(num_meetings=Count('meetings')).filter(num_meetings__eq=0)
    cnt = attendees_to_drop.count()
    if cnt > 0:
        print 'Dropping {0} orphaned Attendees objects.'.format(cnt)
        attendees_to_drop.delete()

