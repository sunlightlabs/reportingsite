import csv

from django.core.management.base import BaseCommand, CommandError

from buckley.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        disclosing_committee_ids = Contribution.objects.order_by('committee').values_list('committee', flat=True).distinct()
        committees = Committee.objects.filter(id__in=disclosing_committee_ids)
        committees.update(has_donors=True)
