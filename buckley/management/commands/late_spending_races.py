"""Races inundated with last-minute spending.
"""
from collections import defaultdict
import csv
import datetime
import sys

from django.core.management.base import BaseCommand, CommandError

from buckley.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        cutoff = datetime.date(2010, 11, 2) - datetime.timedelta(days=14)
        races = defaultdict(dict)
        for i in Expenditure.objects.filter(expenditure_date__lt=cutoff).values('race').annotate(a=Sum('expenditure_amount')):
            races[i['race']]['before'] = i['a']

        for i in Expenditure.objects.filter(expenditure_date__gte=cutoff).values('race').annotate(a=Sum('expenditure_amount')):
            races[i['race']]['after'] = i['a']

        late = [k for k, v in races.iteritems() if v.get('after_cutoff', 0) > v.get('before_cutoff', 0)]

        for i in late:
            x = races[i]
            if x.has_key('before') and x.has_key('after'):
                if x['before'] + x['after'] >= 10000:
                    csv.writer(sys.stdout).writerow(i, x['before'], x['after'], x['before'] + x['after'])
