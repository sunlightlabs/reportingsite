import csv
import sys

from django.core.management.base import BaseCommand, CommandError

from buckley.models import *
from django.db.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        writer = csv.writer(sys.stdout)

        gop_only = []
        dem_only = []

        for committee in Committee.objects.all():
            if not committee.expenditure_set.count():
                continue
            data = committee.expenditure_set.order_by('candidate__party'
                    ).exclude(candidate__party=''
                            ).values('candidate__party', 'support_oppose').annotate(t=Count('pk'))

            d ={'S': {'D': 0, 'R': 0, 'O': 0}, 'O': {'D': 0, 'R': 0, 'O': 0}}

            for row in data:
                """
                [{'support_oppose': u'O', 't': 70, 'candidate__party': u'D'}, {'support_oppose': u'S', 't': 12, 'candidate__party': u'R'}]
                """
                try:
                    d[row['support_oppose']][row['candidate__party']] = row['t']
                except KeyError:
                    try:
                        d[row['support_oppose']]['O'] = row['t']
                    except KeyError:
                        continue

            """
            A group is GOP-only if it supports only Rs
            and does not oppose Rs
            """
            pro_gop = d['S']['R'] + d['O']['D'] # includes anti-dem
            pro_dem = d['S']['D'] + d['O']['R'] # includes anti-gop 

            if pro_gop and not pro_dem:
                gop_only.append(committee)
            elif pro_dem and not pro_gop:
                dem_only.append(committee)

        #print 'GOP Only (%s)' % len(gop_only)
        for committee in gop_only:
            partycmte = 'Yes' if committee.tax_status == 'FECA Party' else 'No'
            writer.writerow(['Republican', committee, committee.expenditure_set.aggregate(t=Sum('expenditure_amount'))['t'], partycmte, ])

        #print 'Dem Only (%s)' % len(dem_only)
        for committee in dem_only:
            partycmte = 'Yes' if committee.tax_status == 'FECA Party' else 'No'
            writer.writerow(['Democratic', committee, committee.expenditure_set.aggregate(t=Sum('expenditure_amount'))['t'], partycmte, ])

