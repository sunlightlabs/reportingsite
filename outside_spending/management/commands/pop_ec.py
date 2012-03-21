import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from dateutil.parser import parse as dateparse
from outside_spending.models import Electioneering_93, Electioneering_94
from outside_spending.management.commands.overlay_utils import *

#cycle=12

class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the electioneering communications table from the independent expenditure csv file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        try:
            cycle = args[0]
        except IndexError:
            print "You must enter a two-digit cycle"
            return
            
        cycle_year = 2000 + int(cycle)
        assert cycle, "You must enter a two-digit cycle"
        
        datafile = "outside_spending/data/%s/ec_exp_20%s.csv" % (cycle, cycle)
        reader = csv.DictReader(open(datafile))
        
        # There are two kinds of records we care about: F93 and F94
        F93=[]
        F94=[]
        for row in reader:
            if row['SRC']=='93':
                F93.append(row)
            elif row['SRC']=='94':
                F94.append(row)
            else:
                print "Unrecognized line type: %s -- skipping " % row['SRC']
                
        # Save the row 93 records first because the 94's refer back to them. 
        
        for f93 in F93:
            print f93
        
            try: 
                ec = Electioneering_93.objects.get(filing_number=f93['REPID'], transaction_id=f93['TRAN_ID'])
            except Electioneering_93.DoesNotExist:
                print "missing!"
                
                this_committee = get_or_create_committee_overlay(f93['COMID'], cycle_year)
                
                ec = Electioneering_93.objects.create(
                        exp_amo=f93['EXP_AMO'],
                        imageno=f93['IMAGENO'],
                        ele_yr=f93['ELE_YR'],
                        receipt_date=dateparse(f93['RECEIPT_DT']),
                        spe_nam=f93['SPE_NAM'],
                        payee=f93['PAY'],
                        purpose=f93['PUR'],
                        exp_date=dateparse(f93['EXP_DAT']),
                        transaction_id=f93['TRAN_ID'],
                        filing_number=f93['REPID'],
                        ele_typ=f93['ELE_TYP'],
                        group_id=f93['GROUP_ID'],
                        fec_id=f93['COMID'],
                        br_tran_id=f93['BR_TRAN_ID'],
                        amnd_ind=f93['AMNDT_IND'],
                        committee=this_committee,
                )
            
        for f94 in F94:
            # get the related 93 line
            ec = Electioneering_93.objects.get(filing_number=f94['REPID'], transaction_id=f94['BR_TRAN_ID'])
            
            try: 
                ec_target = Electioneering_94.objects.get(filing_number=f94['REPID'], transaction_id=f94['TRAN_ID'])
            except Electioneering_94.DoesNotExist:
                print "missing!"
                
                this_candidate = get_or_create_candidate_overlay(f94['CANID'], cycle_year)
                
                
                ec_target = Electioneering_94.objects.create(
                    electioneering=ec,
                    can_id=f94['CANID'],
                    can_name=f94['CAND_NAME'],
                    imageno=f94['IMAGENO'],
                    ele_yr=f94['ELE_YR'],
                    receipt_date=dateparse(f94['RECEIPT_DT']),
                    can_off=f94['CAN_OFF'],
                    can_state=f94['CAN_STATE'],
                    transaction_id=f94['TRAN_ID'],
                    filing_number=f94['REPID'],
                    ele_typ=f94['ELE_TYP'],
                    group_id=f94['GROUP_ID'],
                    fec_id=f94['COMID'],
                    br_tran_id=f94['BR_TRAN_ID'],
                    amnd_ind=f94['AMNDT_IND'],
                    candidate=this_candidate
                )
                    

                # We still need to fix it where candidate ids are missing. 