import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify
from dateutil.parser import parse as dateparse

from rebuckley.models import Expenditure

def clean_currency_field(currency_string):
    cs = currency_string.replace("$","")
    cs= cs.replace(",","")
    result = float(cs)
    return result

class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the expenditure table from the independent expenditure csv file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        cycle = args[0]
        cycle_year = 2000 + int(cycle)
        assert cycle, "You must enter a two-digit cycle"
        
        datafile = "rebuckley/data/%s/IndependentExpenditure_%s.csv" % (cycle, cycle)
        reader = csv.DictReader(open(datafile))
        for row in reader:
            try:
                Expenditure.objects.get(filing_number=row['file_num'],transaction_id=row['tra_id'], )
            
            except Expenditure.DoesNotExist:
                print "Creating expenditure "
                office = ""
                if (len(row['can_id'])>0):
                    this_office = row['can_id'][0]
                
                if (len(row['sup_opp'])>1):
                        row['sup_opp'] = row['sup_opp'][0]
                office=office.strip().upper()
                
                
                #clean_currency_field(row['exp_amo'])
                expenditure = Expenditure.objects.create(
                    cycle=cycle_year,
                    candidate_name=row['can_nam'],
                    image_number = row['ima_num'],
                    raw_committee_id = row['spe_id'].strip().upper(),
                    payee = row['pay'],
                    expenditure_purpose = row['pur'],
                    expenditure_date=dateparse(row['exp_dat']),
                    expenditure_amount=clean_currency_field(row['exp_amo']),
                    support_oppose=row['sup_opp'].strip().upper(),
                    election_type=row['ele_typ'],
                    raw_candidate_id=row['can_id'],
                    office=this_office,
                    state=row['can_off_sta'],
                    district=row['can_off_dis'],
                    transaction_id=row['tra_id'],
                    receipt_date=dateparse(row['rec_dat']),
                    filing_number=row['file_num'],
                    amendment=row['amn_ind'].strip().upper(),
                    electioneering_communication=False
                    )