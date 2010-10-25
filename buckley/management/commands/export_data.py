import csv

from django.core.management.base import BaseCommand, CommandError

from buckley.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        writer = csv.writer(open(r'ie_export_2010-10-25.csv', 'a'))
        for expenditure in Expenditure.objects.filter(electioneering_communication=False).order_by('-expenditure_date'):
            writer.writerow(['committee_id', 'committee', 'candidate_id', 'candidate',
                'payee', 'expenditure_purpose', 'expenditure_date', 'expenditure_amount',
                'support/oppose', 'election_type', 'amendment', 'race', ])
            row = [ expenditure.committee.fec_id(),
                    expenditure.committee,
                    expenditure.candidate.fec_id,
                    expenditure.candidate.fec_name,
                    expenditure.payee.name,
                    expenditure.expenditure_purpose,
                    expenditure.expenditure_date,
                    expenditure.expenditure_amount,
                    expenditure.support_oppose,
                    expenditure.election_type,
                    expenditure.amendment,
                    expenditure.race, ]
            writer.writerow(row)
