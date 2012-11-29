import datetime
import sys

from pprint import pprint

from django.core.management.base import NoArgsCommand

from unicodecsv import UnicodeCsvWriter
from doddfrank.models import Meeting
from doddfrank.views import pivot_table


class Command(NoArgsCommand):
    args = ''
    help = 'Exports a CSV to stdout listing the number of meetings each agency held in each month.'

    def handle(self, *args, **options):
        timespan = {
            'from': datetime.date(2010, 6, 1),
            'to': datetime.date.today()
        }

        print >>sys.stderr, u'Fetching meetings.'
        meetings = [{'yearmonth': '{year}-{month!s:0>2}'.format(year=m.date.year,
                                                                month=m.date.month),
                     'agency': m.agency.initials}
                    for m in Meeting.objects.all()
                    if m.date >= timespan['from']
                    and m.date <= timespan['to']]

        print >>sys.stderr, u'Finding unique key values from among {0} meetings'.format(len(meetings))
        yearmonths = sorted(list(set([m['yearmonth'] for m in meetings])))
        agencies = sorted(list(set([m['agency'] for m in meetings])))
        print >>sys.stderr, unicode(repr(yearmonths))
        print >>sys.stderr, unicode(repr(agencies))

        print >>sys.stderr, u'Creating pivot table.'
        table = pivot_table(objs=meetings,
                            rowfield='agency',
                            colfield='yearmonth',
                            rowkeys=agencies,
                            colkeys=yearmonths,
                            valuefunc=len)

        print >>sys.stderr, u'Writing CSV.'
        writer = UnicodeCsvWriter(sys.stdout)

        header_row = [u'Agency']
        header_row.extend(yearmonths)
        writer.writerow(header_row)

        for rk in agencies:
            row = [rk]
            for ck in yearmonths:
                row.append(unicode(table[rk][ck]))
            writer.writerow(row)

