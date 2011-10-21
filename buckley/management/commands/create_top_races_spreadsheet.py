import csv

from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from buckley.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        senate_races = Expenditure.objects.filter(election_type='G', race__contains='Senate').values('race').annotate(amt=Sum('expenditure_amount')).order_by('-amt')[:10]
        csv.DictWriter(open(r'senate_outside_spending.csv', 'w'), fieldnames=['race', 'amt', ]).writerows(senate_races)
        house_races = Expenditure.objects.filter(election_type='G').exclude(race__contains='Senate').values('race').annotate(amt=Sum('expenditure_amount')).order_by('-amt')[:10]
        csv.DictWriter(open(r'house_outside_spending.csv', 'w'), fieldnames=['race', 'amt', ]).writerows(house_races)

        races = list(senate_races) + list(house_races)
        for race in races:
            print race
            spending = Expenditure.objects.filter(election_type='G', race=race['race']).order_by('committee__name').values('committee__name').annotate(amt=Sum('expenditure_amount')).order_by('-amt')
            csv.DictWriter(open(r'%s.csv' % race['race'], 'w'), fieldnames=['committee__name', 'amt']).writerows(spending)
