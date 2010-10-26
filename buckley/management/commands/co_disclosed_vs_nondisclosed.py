import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from buckley.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        races = Expenditure.objects.order_by('race').values_list('race', flat=True).filter(race__startswith='CO').distinct()
        data = dict([(x, {'disclosers': 0, 'nondisclosers': 0}) for x in races])
        writer = csv.writer(sys.stdout)
        for race in races:
            non_discloser_ids = Expenditure.objects.filter(race=race, committee__has_donors=False).exclude(committee__tax_status='FECA Party').order_by('committee').values_list('committee', flat=True)
            non_disclosers = Committee.objects.filter(id__in=non_discloser_ids)
            for committee in non_disclosers:
                amount = committee.expenditure_set.filter(race=race).aggregate(a=Sum('expenditure_amount'))['a']
                writer.writerow([race, committee, amount, 'N'])
                data[race]['nondisclosers'] += amount

            discloser_ids = Expenditure.objects.filter(race=race, committee__has_donors=True).exclude(committee__tax_status='FECA Party').order_by('committee').values_list('committee', flat=True)
            disclosers = Committee.objects.filter(id__in=discloser_ids)
            for committee in disclosers:
                amount = committee.expenditure_set.filter(race=race).aggregate(a=Sum('expenditure_amount'))['a']
                writer.writerow([race, committee, amount, 'Y'])
                data[race]['disclosers'] += amount

        print
        print
        for k, v in data.iteritems():
            writer.writerow([k, v['disclosers'], v['nondisclosers'], ])
