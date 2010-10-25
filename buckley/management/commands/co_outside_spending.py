import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db.models import *

from buckley.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        expenditures = Expenditure.objects.filter(race__startswith = 'CO').order_by('expenditure_date')

        writer = csv.writer(sys.stdout)
        writer.writerow(['Type', 'Committee', 'Race', 'Candidate', 'Amount',
                         'Purpose', 'Payee', 'Support/Oppose',
                         'Election type', 'Expenditure date', ])

        for expenditure in expenditures:
            if expenditure.electioneering_communication:
                candidate = ' || '.join([str(x) for x in expenditure.electioneering_candidates.all()])
                support_oppose = ''
                expenditure_type = 'EC'
            else:
                candidate = expenditure.candidate
                support_oppose = expenditure.support_oppose
                expenditure_type = 'IE'

            row = [expenditure_type,
                   expenditure.committee,
                   expenditure.race,
                   candidate,
                   expenditure.expenditure_amount,
                   expenditure.expenditure_purpose,
                   expenditure.payee,
                   expenditure.support_oppose,
                   expenditure.election_type,
                   expenditure.expenditure_date, ]
            writer.writerow(row)
