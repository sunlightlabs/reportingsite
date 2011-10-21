import csv
import sys

from django.core.management.base import BaseCommand, CommandError

from buckley.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        cids = ['C30001648',
                'C90011552',
                'C90011289',
                'C90009358',
                'C90011438',
                'C90011677',
                'C30001028',
                'C90011214',
                'C90005927',
                'C90009739',
                'C30001457',
                'C30001051',
                'C00438747',
                'C90011693',
                'C90009994', ]
        writer = csv.writer(sys.stdout)
        writer.writerow(['committee_id', 'committee', 'race', 'candidate', 'amount',
            'purpose', 'payee', 'support/oppose', 'election_type', 'expenditure_date', ])

        for cid in cids:
            try:
                committee_id = CommitteeId.objects.get(fec_committee_id=cid)
            except CommitteeId.DoesNotExist:
                continue
            committee = committee_id.committee
            for expenditure in committee.expenditure_set.all():
                row = [cid,
                        committee,
                        expenditure.race,
                        expenditure.candidate,
                        expenditure.expenditure_amount,
                        expenditure.expenditure_purpose,
                        expenditure.payee,
                        expenditure.support_oppose,
                        expenditure.election_type,
                        expenditure.expenditure_date, ]
                writer.writerow(row)

