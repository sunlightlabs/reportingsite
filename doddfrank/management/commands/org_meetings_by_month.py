import datetime
import sys

from pprint import pprint

from django.core.management.base import BaseCommand

from unicodecsv import UnicodeCsvWriter
from doddfrank.models import Meeting
from doddfrank.views import pivot_table


class Command(BaseCommand):
    args = ''
    help = 'Exports a CSV to stdout listing the number of meetings each agency held in each month.'

    def handle(self, *args, **options):
        timespan = {
            'from': datetime.date(2010, 6, 1),
            'to': datetime.date.today()
        }

        orgs_of_interest = set()
        for arg in args:
            with file(arg, 'r') as fil:
                for line in fil:
                    line = line.decode('utf-8').strip()
                    if line:
                        orgs_of_interest.add(line)
        orgs_of_interest = list(orgs_of_interest)
        lower_orgs_of_interest = [o.lower() for o in orgs_of_interest]
        print >>sys.stderr, u'{0} organizations of interest.'.format(len(orgs_of_interest))

        print >>sys.stderr, u'Fetching meetings.'

        attendances = [{'yearmonth': '{year}-{month!s:0>2}'.format(year=m.date.year,
                                                                   month=m.date.month),
                        'org': org.name}
                       for m in Meeting.objects.all()
                       for org in m.organizations.all()
                       if (len(orgs_of_interest) == 0
                           or org.name.lower().strip() in lower_orgs_of_interest)
                       and m.date >= timespan['from']
                       and m.date <= timespan['to']]

        print >>sys.stderr, u'Finding unique key values from among {0} attendances'.format(len(attendances))
        yearmonths = sorted(list(set([m['yearmonth'] for m in attendances])))
        orgs = sorted(list(set([m['org'] for m in attendances])))
        print >>sys.stderr, unicode(repr(yearmonths))
        print >>sys.stderr, unicode(repr(orgs))

        print >>sys.stderr, u'Creating pivot table.'
        table = pivot_table(objs=attendances,
                            rowfield='org',
                            colfield='yearmonth',
                            rowkeys=orgs,
                            colkeys=yearmonths,
                            valuefunc=len)

        print >>sys.stderr, u'Writing CSV.'
        writer = UnicodeCsvWriter(sys.stdout)

        header_row = [u'Organization']
        header_row.extend(yearmonths)
        writer.writerow(header_row)

        for rk in orgs:
            row = [rk]
            for ck in yearmonths:
                row.append(unicode(table[rk][ck]))
            writer.writerow(row)
            if rk in orgs_of_interest:
                orgs_of_interest.remove(rk)

        if len(orgs_of_interest) > 0:
            print >>sys.stderr, u'Organizations of interest that were not found in the database:'
            for org in sorted(orgs_of_interest):
                print >>sys.stderr, org


