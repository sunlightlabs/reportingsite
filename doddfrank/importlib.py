import sys
import hashlib
import json
import re

from copy import deepcopy
from StringIO import StringIO

import requests
import progressbar
import dateutil.parser

from django.db.models import Count

from doddfrank.models import (Agency, Meeting, Attendee,
                              Organization,
                              OrganizationNameCorrection,
                              OrganizationBlacklist,
                              ScrapingError)


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


def import_meetings(meetings, keyfunc, copyfunc, update_existing=False):
    """
    meetings is a list of objects pulled from ScraperWiki

    keyfunc is a function of a record and the hash of that record.
    It should return a dictionary suitable for selecting a unique
    database record.

    copyfunc is a function of a record and a Meeting object. It
    should copy fields from the record to the appropriate fields
    of the database object.

    TODO: Add an argument that enables updating existing objects.
          This is needed if the copyfunc function is changed.
    """

    progress = progressbar.ProgressBar()
    for m in progress(meetings):
        m_hash = dict_hash(m)
        keys = keyfunc(m, m_hash)
        (meeting, created) = Meeting.objects.get_or_create(**keys)
        if created or update_existing:
            copyfunc(m, meeting)
            meeting.import_hash = m_hash
            if update_existing:
                meeting.organizations.all().delete()
                meeting.attendees.all().delete()
            meeting.save()


def import_attendees(meetings, attendees, shared_keys,
                     keyfunc, copyfunc,
                     meeting_keyfunc, meeting_copyfunc,
                     org_field,
                     update_existing=False):
    """
    This function mimics an inner join between the attendees records and the
    metings records in order to create Attendee objectss and link them to the
    the corresponding Meeting objects.

    meetings and attendees are both lists of objects pulled from ScraperWiki

    keyfunc is a function of an attendee record and the hash of that record.
    It should return a dictionary suitable for selecting a unique
    Attendee object.

    copyfunc is a function of an attendee record and an Attendee object. 
    It should copy fields from the attendee record to the appropriate fields
    of the Attendee object.
    """

    meeting_index = index_dict_list(meetings, shared_keys)
    get_shared_keys = DictSlicer(*shared_keys)
    progress = progressbar.ProgressBar()
    for a in progress(attendees):
        a_hash = dict_hash(a)
        m_index_key = dict_hash(get_shared_keys(a))
        m = meeting_index[m_index_key]

        m_hash = dict_hash(m)
        m_keys = meeting_keyfunc(m, m_hash)
        meeting = Meeting.objects.get(**m_keys)

        org_name = a.get(org_field)
        if org_name and organization_is_blacklisted(org_name):
            continue
        if org_name:
            org_name = standardized_organization_name(org_name.strip())
        if org_name:
            org_name = correct_organization_name(org_name)
        if org_name and organization_is_blacklisted(org_name):
            continue
        if org_name:
            (org, created) = Organization.objects.get_or_create(name=org_name)
            if created:
                org.save()
            meeting.organizations.add(org)
        else:
            org = None

        a_keys = keyfunc(a, a_hash)
        (attendee, created) = Attendee.objects.get_or_create(org=org, **a_keys)
        if created or update_existing:
            copyfunc(a, attendee)
            attendee.org = org
            attendee.import_hash = a_hash
            attendee.save()
        meeting.attendees.add(attendee)
        meeting.save()


def import_organizations(meetings, organizations, shared_keys,
                         org_field, meeting_keyfunc):
    """
    This function mimics an inner join between the organizations records and the
    meetings records in order to create Organization objects and link them to the
    the corresponding Meeting objects.

    meetings and organizations are both lists of objects pulled from ScraperWiki
    """

    meeting_index = index_dict_list(meetings, shared_keys)
    get_shared_keys = DictSlicer(*shared_keys)
    progress = progressbar.ProgressBar()
    for o in progress(organizations):
        if o.get(org_field, '').strip():
            m_index_key = dict_hash(get_shared_keys(o))
            m = meeting_index[m_index_key]

            m_hash = dict_hash(m)
            m_keys = meeting_keyfunc(m, m_hash)
            meeting = Meeting.objects.get(**m_keys)

            org_name = o.get(org_field).strip()
            if org_name and organization_is_blacklisted(org_name):
                continue
            if org_name:
                org_name = standardized_organization_name(org_name.strip())
            if org_name:
                org_name = correct_organization_name(org_name)
            if org_name and organization_is_blacklisted(org_name):
                continue
            if org_name:
                (org, created) = Organization.objects.get_or_create(name=org_name)
                if created:
                    org.save()
                meeting.organizations.add(org)


def organization_is_blacklisted(org_name):
    try:
        org = OrganizationBlacklist.objects.get(name=org_name)
        return True
    except OrganizationBlacklist.DoesNotExist:
        return False


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


def prune_organizations():
    """
    Similar to the prune_attendees function, this function removes
    Organization objects that are not associated with any meetings
    or attendees.
    """
    orgs_to_drop = Organization.objects.annotate(mcnt=Count('meetings'), acnt=Count('representatives')).filter(mcnt=0, acnt=0)
    cnt = orgs_to_drop.count()
    if cnt > 0:
        print 'Dropping {0} orphaned Organization objects.'.format(cnt)
        orgs_to_drop.delete()


def correct_organization_name(name):
    try:
        correction = OrganizationNameCorrection.objects.get(original=name)
        return correction.replacement
    except OrganizationNameCorrection.DoesNotExist:
        return name


BasicUnicodeToAscii = {
    u'\xa0': ' ',

    u'\u007e': '~',
    u'\u00a0': ' ',
    u'\u00a9': '(C)',
    u'\u00aE': '(R)',

    u'\u2000': '',
    u'\u2001': '',
    u'\u2002': '',
    u'\u2003': '',
    u'\u2004': '',
    u'\u2005': '',
    u'\u2006': '',
    u'\u2007': '',
    u'\u2008': '',
    u'\u2009': '',
    u'\u200A': '',
    u'\u200B': '',
    u'\u200C': '',
    u'\u200D': '',
    u'\u200E': '',
    u'\u200F': '',

    u'\u2010': '-',
    u'\u2011': '-',
    u'\u2012': '-',
    u'\u2013': '-',
    u'\u2014': '--',
    u'\u2015': '--',
    u'\u2016': '||',
    u'\u2017': '_',
    u'\u2018': '\'',
    u'\u2019': '\'',
    u'\u201A': '\'',
    u'\u201B': '\'',
    u'\u201C': '"',
    u'\u201D': '"',
    u'\u201E': '"',
    u'\u201F': '"',

    u'\u2020': '+',
    u'\u2021': '+',
    u'\u2022': '*',
    u'\u2023': '>',
    u'\u2024': '.',
    u'\u2025': '..',
    u'\u2026': '...',
    u'\u2027': '*',
    u'\u2028': '\n',
    u'\u2029': '\n',
    u'\u202A': '',
    u'\u202B': '',
    u'\u202C': '',
    u'\u202D': '',
    u'\u202E': '',
    u'\u202F': ' ',

    u'\u2030': '%%',
    u'\u2031': '%%%',
    u'\u2032': '\'',
    u'\u2033': '\'\'',
    u'\u2034': '\'\'\'',
    u'\u2035': '`',
    u'\u2036': '``',
    u'\u2037': '```',
    u'\u2038': '^',
    u'\u2039': '<',
    u'\u203A': '>',
    u'\u203B': 'x',
    u'\u203C': '!!',
    u'\u203D': '?',
    u'\u203E': '-',
    u'\u203F': '_'
}
def substitute_characters(s, subs=BasicUnicodeToAscii):
    chars = []
    for c in s:
        chars.append(subs.get(c, c))
    return u"".join(chars)


def strip_whitespace(s, also=u''):
    return s.strip(u' \t\u00a0' + also)


CompanySuffixPattern1 = re.compile(r'[,]? (LLC|LLP|MLP|Corp(?:oration)?|Inc|N[.]?A[.]?)[.]?', re.IGNORECASE)
CompanySuffixPattern2 = re.compile(r'& Co(?:mpany|\.)?\b', re.IGNORECASE)
CompanySuffixPattern3 = re.compile(r'(^The |\bGroup\b)', re.IGNORECASE)
ConsequtiveSpacesPattern = re.compile(r'\s{2,}', re.UNICODE)
def fix_company_suffixes(s):

    # Remove company structure suffixes
    t = CompanySuffixPattern1.sub(r' ', s)
    t = strip_whitespace(t)

    words = re.split(r'\s+', t)
    if len(words) > 3:
        # Drop '& Company' from longer names
        u = CompanySuffixPattern2.sub(r' ', t)
    else:
        # For short names, standardize to '& Co'
        u = CompanySuffixPattern2.sub(r'& Co', t)
    u = strip_whitespace(u)

    v = CompanySuffixPattern3.sub(r'', u)
    v = strip_whitespace(v)

    w = ConsequtiveSpacesPattern.sub(r' ', v)
    w = strip_whitespace(w, also=u'.')
    return w
    

OrgNameCharacterSubs = deepcopy(BasicUnicodeToAscii)
def standardized_organization_name(name):
    OrgNameCharacterSubs[u'\u201f'] = '\'' # A name should never have double quotes
    
    normalized = substitute_characters(name, OrgNameCharacterSubs)
    return fix_company_suffixes(normalized)


def import_scraping_errors(agency, errors):
    for error in errors:
        for key in ('url', 'agency', 'description', 'context'):
            if key not in error:
                print >>sys.stderr, u'Key ({0}) missing from error record.'.format(key)
                continue

        (error, created) = ScrapingError.objects.get_or_create(agency=agency, url=error['url'])
        error.description = error['description']
        error.context = error['context']
        error.timestamp = error['timestamp']
        error.save()


class ObjectCounts(object):
    def __init__(self, agency, *args, **kwargs):
        self.agency = agency
        self.values = {}
        self.update()
        self.previous_values = deepcopy(self.values)

    def update(self):
        self.previous_values = deepcopy(self.values)

        self.values['meetings'] = Meeting.objects.count()
        self.values['orgs'] = Organization.objects.count()
        self.values['attendees'] = Attendee.objects.count()

        self.values['ag_meetings'] = Meeting.objects.filter(agency=self.agency).count()
        self.values['ag_orgs'] = Organization.objects.filter(meetings__agency=self.agency).count()
        self.values['ag_attendees'] = Attendee.objects.filter(meetings__agency=self.agency).count()

        return self

    def diffstat(self):
        buf = StringIO()
        buf.write(u'{0!s: <10} {1!s: >6} {2!s: >6} {3!s: >9} {4!s: >6}\n'.format(u'Object', u'Count', u'(diff)', u'for Ag.', u'(diff)'))

        for k in sorted(self.values.keys()):
            if k.startswith('ag_') == False:
                v = self.values[k]
                ag_v = self.values['ag_' + k]

                diff = unicode(v - self.previous_values.get(k, 0))
                ag_diff = unicode(ag_v - self.previous_values.get('ag_' + k, 0))
                
                diff = u'+' + diff if not diff.startswith(u'-') else diff
                ag_diff = u'+' + ag_diff if not ag_diff.startswith(u'-') else ag_diff

                buf.write(u'{0!s: <10} {1!s: >6} {2!s: >6} {3!s: >9} {4!s: >6}\n'.format(k, v, diff, ag_v, ag_diff))

        return buf.getvalue()

    def __unicode__(self):
        buf = StringIO()
        buf.write(u'{0!s: <10} {1!s: >6} {2!s: >9}\n'.format(u'Object', u'Count', u'for Ag.'))

        for k in sorted(self.values.keys()):
            if k.startswith('ag_') == False:
                v = self.values[k]
                ag_v = self.values['ag_' + k]
                buf.write(u'{0!s: <10} {1!s: >6} {2!s: >9}\n'.format(k, v, ag_v))

        return buf.getvalue()

