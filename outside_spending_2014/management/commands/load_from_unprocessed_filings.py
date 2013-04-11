"""Enter IE data from forms 24, 5, 3 and 9 from unprocessed filings"""

from time import sleep

from django.core.management.base import BaseCommand

from outside_spending_2014.form_parser import form_parser
from outside_spending_2014.read_FEC_settings import FILECACHE_DIRECTORY
from fec_alerts.models import new_filing

from form_helpers import process_F24, process_F3X, process_F3X_contribs, process_file
from fec_alerts.utils.fec_logging import fec_logger

# 835788

class Command(BaseCommand):
    
    def __init__(self):
        self.fp = form_parser()
        self.FEClogger=fec_logger()
        

    def handle(self, *args, **options):

        self.FEClogger.info('LOAD_FROM_UNPROCESSED_FILINGS - starting regular run')
        new_filings = new_filing.objects.filter(filing_is_parsed=False).order_by('filing_number')

        for filing in new_filings:
            print "Need to process filing %s" % (filing.filing_number)
            # only process forms we care about -- we need to process all F3X's though, because anyone might make IEs
            if filing.form_type in ('F3XN', 'F3XA', 'F3XT', 'F24N', 'F24A', 'F5N', 'F5A'):
                process_file(filing.filing_number, self.fp)
                sleep(1)
                
            filing.filing_is_parsed=True
            filing.save()
            