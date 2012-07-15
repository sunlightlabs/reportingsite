"""Special case: pull IE's from a monthly F5 form. In general we pull these from a 24-hour notice form, and then don't pull them from the monthly versions because AAN has argued that they don't need to appear on the monthly forms. However American Future Fund has taken the reverse tack thus far, and has even filed on paper. """

# Known instances: 796425

from time import sleep

from django.core.management.base import BaseCommand

from outside_spending.form_parser import form_parser
from outside_spending.outside_spending_settings import filecache_directory
from outside_spending.models import unprocessed_filing

from form_helpers import process_monthly_F5_contribs
from outside_spending.utils.fec_logging import fec_logger


class Command(BaseCommand):
    
    def __init__(self):
        self.fp = form_parser()
        self.FEClogger=fec_logger()
        

    def handle(self, *args, **options):

        self.FEClogger.info('LOAD_MONTHLY_F5_MANUALLY - starting human triggered run')
        filing_numbers = [796425]
        for filing_number in filing_numbers:
            process_monthly_F5_contribs(filing_number, self.fp)
            sleep(1)
                

            