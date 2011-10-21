import csv

from django.core.management.base import BaseCommand, CommandError

from buckley.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        writer = csv.writer(open(r'americans_for_prosperity_spending.csv', 'a'))

        writer.writerow(['committee_id', 'committee', 'candidate_id', 'candidate',
            'payee', 'expenditure_purpose', 'expenditure_date', 'expenditure_amount',
            'support/oppose', 'election_type', 'amendment', 'race', 'filing_number', ])
        
        committee = Committee.objects.get(slug='americans-for-prosperity')
        for expenditure in committee.expenditure_set.all():
            if expenditure.electioneering_communication:
                row = [ 'EC',
                        expenditure.committee.fec_id(),
                        expenditure.committee,
                        ', '.join(['%s (%s)' % (str(x), x.party) for x in expenditure.electioneering_candidates.all()]),
                        expenditure.payee,
                        expenditure.expenditure_purpose,
                        expenditure.expenditure_date,
                        expenditure.expenditure_amount,
                        '',
                        expenditure.election_type,
                        expenditure.race,
                        expenditure.filing_number,
                        ]
            else:
                row = [ 'IE',
                        expenditure.committee.fec_id(),
                        expenditure.committee,
                        '%s (%s)' % (expenditure.candidate, expenditure.candidate.party),
                        expenditure.payee,
                        expenditure.expenditure_purpose,
                        expenditure.expenditure_date,
                        expenditure.expenditure_amount,
                        expenditure.support_oppose,
                        expenditure.election_type,
                        expenditure.race,
                        expenditure.filing_number,
                        ]
            writer.writerow(row)
            print row

