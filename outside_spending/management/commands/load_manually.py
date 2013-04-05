"""Enter IE data from forms 24, 5, 3 and 9 from unprocessed filings"""

from time import sleep

from django.core.management.base import BaseCommand

from outside_spending.form_parser import form_parser
from outside_spending.outside_spending_settings import filecache_directory
from outside_spending.models import unprocessed_filing

from form_helpers import process_F24, process_F3X, process_F3X_contribs, process_file
from outside_spending.utils.fec_logging import fec_logger


class Command(BaseCommand):
    
    def __init__(self):
        self.fp = form_parser()
        self.FEClogger=fec_logger()
        

    def handle(self, *args, **options):

        self.FEClogger.info('LOAD_MANUALLY - starting human triggered run')
        filing_numbers = [846635]
        for filing_number in filing_numbers:
            process_file(filing_number, self.fp)
            sleep(1)
                

            