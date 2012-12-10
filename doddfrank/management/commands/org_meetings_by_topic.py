import datetime
import sys
import re
import itertools

from pprint import pprint
from itertools import chain

from django.core.management.base import BaseCommand
from optparse import make_option

from unicodecsv import UnicodeCsvWriter, UnicodeCsvReader
from doddfrank.models import Meeting
from doddfrank.views import pivot_table

def strip_whitespace(s, also=u''):
    return s.strip(u' \t\u00a0' + also)

class flattened(object):
    """An iterator class that automatically chains sub-iterators."""

    def __init__(self, iterable, as_is=(str, unicode, bytes)):
        self.iterator = iter(iterable)
        self.as_is = as_is

    def __iter__(self):
        return self

    def next(self):
        item = self.iterator.next()
        
        if not isinstance(item, self.as_is):
            try:
                new_iter = iter(item)
                self.iterator = itertools.chain(new_iter, self.iterator)
                return self.next()
            except TypeError:
                pass
        
        return item

def firstof(*args):
    for a in args:
        if a is not None:
            return a
    return None

def unique(it):
    return dict.fromkeys(it, None).keys()

def build_topic_map(path):
    topic_map = {}
    with file(path) as csvfile:
        reader = UnicodeCsvReader(csvfile)
        for row in reader:
            topic = strip_whitespace(row[0])
            for cell in row:
                cell = strip_whitespace(cell)
                if cell:
                    topic_list = topic_map.get(cell, [])
                    if topic not in topic_list:
                        topic_list.append(topic)
                        topic_map[cell] = topic_list
    return topic_map

def corrected_topic(topic_map, topic):
    if topic in topic_map:
        return topic_map.get(topic)
    else:
        return [topic]

sep_pattern = re.compile(ur'\s*[;\r\n]+\s*')
def split_topics(topic_map, meeting):
    topics = [strip_whitespace(t) for t in sep_pattern.split(meeting.topic or meeting.subcategory or meeting.category)]
    corrected_topics = [corrected_topic(topic_map, topic) for topic in topics]
    flattened_topics = [strip_whitespace(t) for t in flattened(corrected_topics)]
    unique_topics = unique(flattened_topics)
    return unique_topics

class Command(BaseCommand):
    args = ''
    help = 'Exports a CSV to stdout listing the number of meetings held each month grouped by the topic discussed.'
    option_list = BaseCommand.option_list + (
        make_option('--topicmap', action='store', dest='topicmap', metavar='FILE',
                    default=None, help='Use this topic map.'),
        make_option('--agency', action='store', dest='agency', metavar='AGENCY',
                    default=None, help='Limit the queries to this agency.'),
    )

    def handle(self, *args, **options):
        timespan = {
            'from': datetime.date(2010, 6, 1),
            'to': datetime.date.today()
        }

        topic_map = {}
        if options['topicmap']:
            topic_map = build_topic_map(options['topicmap'])
            pprint(topic_map, stream=sys.stderr)

        orgs_of_interest = set()
        for arg in args:
            with file(arg, 'r') as fil:
                for line in fil:
                    line = line.decode('utf-8').strip()
                    if line:
                        orgs_of_interest.add(line)
        orgs_of_interest = list(orgs_of_interest)
        lower_orgs_of_interest = [o.lower() for o in orgs_of_interest]
        if len(orgs_of_interest) > 0:
            print >>sys.stderr, u'{0} organizations of interest.'.format(len(orgs_of_interest))

        print >>sys.stderr, u'Fetching meetings.'

        meetings = Meeting.objects.filter(date__gte=timespan['from'],
                                          date__lte=timespan['to'])
        agency = options.get('agency')
        if agency is not None:
            meetings = meetings.filter(agency__initials__iexact=agency)

        discussions = [{'org': o.name,
                        'topic': t}
                       for m in meetings
                       for o in m.organizations.all()
                       if (len(orgs_of_interest) == 0
                           or o.name.lower().strip() in lower_orgs_of_interest)
                       for t in split_topics(topic_map, m)]

        print >>sys.stderr, u'Finding unique key values from among {0} discussions'.format(len(discussions))
        orgs = sorted(list(set([m['org'] for m in discussions])))
        topics = sorted(list(set([m['topic'] for m in discussions])))
        print >>sys.stderr, unicode(repr(orgs))
        print >>sys.stderr, unicode(repr(topics))

        print >>sys.stderr, u'Creating pivot table.'
        table = pivot_table(objs=discussions,
                            rowfield='org',
                            colfield='topic',
                            rowkeys=orgs,
                            colkeys=topics,
                            valuefunc=len)

        print >>sys.stderr, u'Writing CSV.'
        writer = UnicodeCsvWriter(sys.stdout)

        header_row = [u'Organization']
        header_row.extend(topics)
        header_row.append(u'Total')
        writer.writerow(header_row)

        for rk in orgs:
            row = [rk]
            row_total = 0
            for ck in topics:
                row.append(unicode(table[rk][ck]))
                row_total += table[rk][ck] or 0
            row.append(unicode(row_total))
            writer.writerow(row)
            if rk in orgs_of_interest:
                orgs_of_interest.remove(rk)

        if len(orgs_of_interest) > 0:
            print >>sys.stderr, u'Organizations of interest that were not found in the database:'
            for org in sorted(orgs_of_interest):
                print >>sys.stderr, org



