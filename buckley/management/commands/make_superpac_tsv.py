import csv
import sys

from django.core.management.base import BaseCommand, CommandError

from buckley.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        writer = csv.writer(sys.stdout, delimiter='\t')
        headers = ['Committee','Amount','Support/Oppose','Candidate','Party','Race',]
        writer.writerow(headers)
        ieonly_ids = [x.pk for x in IEOnlyCommittee.objects.all() if x.has_expenditures()]
        committee_ids = CommitteeId.objects.filter(fec_committee_id__in=ieonly_ids)
        committees = Committee.objects.filter(pk__in=[x.committee.pk for x in committee_ids])
        for committee in committees:
            for i in committee.all_candidates_with_amounts():
                writer.writerow([committee,] + i.values())
        
