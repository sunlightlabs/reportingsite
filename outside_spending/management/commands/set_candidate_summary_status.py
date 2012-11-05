import gspread

from datetime import date
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError
from outside_spending.models import Candidate_Overlay
from django.conf import settings
from overlay_utils import get_or_create_candidate_overlay

GOOGLE_SPREADSHEET_USERNAME = settings.GOOGLE_SPREADSHEET_USERNAME
GOOGLE_SPREADSHEET_PASSWORD = settings.GOOGLE_SPREADSHEET_PASSWORD

class Command(BaseCommand):
    help = "Set details in the candidate overlay from a google spreadsheet. "
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        gc = gspread.login(GOOGLE_SPREADSHEET_USERNAME,GOOGLE_SPREADSHEET_PASSWORD)
        doc_name = 'candidates2'
        # Open a worksheet from spreadsheet with one shot
        wks = gc.open(doc_name).sheet1
        worksheet_data = wks.get_all_values()
        # preelection reports are through: I think senate is updated... 
        #update_date = date(2012,10,17)
        
        # ignore header row
        for row in worksheet_data[1:]:
            #print row
            fec_id = row[0]
            cand_ici = row[3]
            total_receipts = row[11]
            total_disbursements = row[12]
            ending_cash = row[13]
            ttl_ind_contribs = row[14]
            cand_contrib = row[15]
            cand_loans = row[16]
            debts_owed_by = row[17]
            update_date = dateparse(row[18])
            
            #print "fec_id %s name %s cand_ici %s tot_recpts %s totl_contribs %s" % (fec_id, row[1], cand_ici, total_receipts, ttl_ind_contribs)
            
            try:
                co = get_or_create_candidate_overlay(fec_id, 12)
                co.cand_ici = cand_ici
                co.is_general_candidate = True
                co.cand_ttl_receipts = total_receipts
                co.cand_total_disbursements = total_disbursements
                co.cand_ending_cash = ending_cash
                co.cand_ttl_ind_contribs = ttl_ind_contribs
                co.cand_cand_contrib = cand_contrib
                co.cand_cand_loans = cand_loans
                co.cand_debts_owed_by = debts_owed_by                                                         
                co.cand_report_date =  update_date               
                co.save()                                                                             
                
            except Candidate_Overlay.DoesNotExist:
                print "Missing candidate %s fec_id = '%s' " % (row[1], fec_id)