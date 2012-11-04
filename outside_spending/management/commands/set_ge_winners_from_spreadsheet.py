import gspread

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from outside_spending.models import Candidate_Overlay
from django.conf import settings

GOOGLE_SPREADSHEET_USERNAME = settings.GOOGLE_SPREADSHEET_USERNAME
GOOGLE_SPREADSHEET_PASSWORD = settings.GOOGLE_SPREADSHEET_PASSWORD

class Command(BaseCommand):
    help = "Set general election winners from a hand-maintained google spreadsheet. "
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        gc = gspread.login(GOOGLE_SPREADSHEET_USERNAME,GOOGLE_SPREADSHEET_PASSWORD)
        doc_name = 'election_results'
        # Open a worksheet from spreadsheet with one shot
        wks = gc.open(doc_name).sheet1
        
        worksheet_data = wks.get_all_values()
        directions_row = worksheet_data[0]
        row_headers = worksheet_data[1]
        data_rows = worksheet_data[2:]

        for row in data_rows:
            (fec_id, winner, name, party, office, state, district) = row[:7]
            iserror=False
            iswinner = False
            if winner:
                try:
                    if int(winner)==1:
                        print "Found winner %s, %s" % (winner, fec_id)
                        iswinner = True
                        try:
                            co = Candidate_Overlay.objects.get(fec_id=fec_id)
                            if not co.cand_is_gen_winner:
                                co.cand_is_gen_winner = True
                                co.save()
                            
                        except Candidate_Overlay.DoesNotExist:
                            print "Warning: missing winning candidate %s fec_id = '%s' " % (row[1], fec_id)
                        
                    else:
                        iserror=True
                except ValueError:
                    iserror=True
            if iserror:
                print "warning: odd value in winner colwinner: %s" % (winner)
            if not iswinner:
                try:
                    co = Candidate_Overlay.objects.get(fec_id=fec_id)
                    if co.cand_is_gen_winner:
                        co.cand_is_gen_winner = False
                        co.save()
                    
                except Candidate_Overlay.DoesNotExist:
                    pass
                    

        # Now set the update time
        update_string = datetime.now().strftime("%Y-%m-%d %H:%M") + " UTC"
        wks.update_cell(3, 10, update_string)