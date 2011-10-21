import csv

from django.core.management.base import BaseCommand, CommandError

from buckley.models import *

def testing():
    expenditures = Expenditure.objects.filter(committee__has_donors=False).exclude(committee__tax_status='FECA Party').order_by('committee', 'expenditure_date')

class Command(BaseCommand):
    def handle(self, *args, **options):
        writer = csv.writer(open(r'non_disclosure_spending.csv', 'a'))

        writer.writerow(['committee_id', 'committee', 'candidate_id', 'candidate',
            'payee', 'expenditure_purpose', 'expenditure_date', 'expenditure_amount',
            'support/oppose', 'election_type', 'amendment', 'race', 'filing_number', ])

        expenditures = Expenditure.objects.filter(committee__has_donors=False).exclude(committee__tax_status='FECA Party').order_by('committee', 'expenditure_date')
        for expenditure in expenditures:
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


        
        return
        for committee in Committee.objects.filter(has_donors=False).exclude(tax_status='FECA Party'):

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

