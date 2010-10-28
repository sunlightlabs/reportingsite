import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from buckley.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        races = Expenditure.objects.order_by('race').values_list('race', flat=True).distinct()
        for race in races:
            amt = Expenditure.objects.filter(race=race, committee__has_donors=False).aggregate(a=Sum('expenditure_amount'))['a']
            if amt and race:
                csv.writer(sys.stdout).writerow([race, amt, ])
