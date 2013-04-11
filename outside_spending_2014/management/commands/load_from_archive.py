"""Enter IE data from forms 24, 5, 3 and 9 from unprocessed filings"""
import os
from time import sleep

from django.core.management.base import BaseCommand

from outside_spending_2014.form_parser import form_parser
from outside_spending_2014.read_FEC_settings import FILECACHE_DIRECTORY
from fec_alerts.models import new_filing

from form_helpers import process_F24, process_F3X, process_F3X_contribs, process_file
from fec_alerts.utils.fec_logging import fec_logger


def get_file_list(filemin=843366, list_length=50000):
    filecount = 0
    arraylist = []
    for d, _, files in os.walk(FILECACHE_DIRECTORY):
        for a in files:
            filingnum = a.replace(".fec", "")
            
            try:
                if int(filingnum) < filemin:
                    continue
                filecount += 1
                if filecount > list_length:
                    break
                arraylist.append(filingnum)
            except ValueError:
                continue
    return arraylist
    
    
    
class Command(BaseCommand):
    
    def __init__(self):
        self.fp = form_parser()
        self.FEClogger=fec_logger()
        

    def handle(self, *args, **options):

        self.FEClogger.info('LOAD_FROM_ ARCHIVED _FILINGS - starting run')
        new_filings = get_file_list()

        for this_filing in new_filings:
            print "Need to process filing %s" % (this_filing)
            # only process forms we care about -- we need to process all F3X's though, because anyone might make IEs
            
            process_file(this_filing, self.fp)

            