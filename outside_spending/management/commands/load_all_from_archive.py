"""Enter IE data from forms 24, 5, 3 and 9 from the archive"""

import re
import os

from django.core.management.base import BaseCommand

from outside_spending.form_parser import form_parser
#from outside_spending.filing import filing
#from outside_spending.models import Filing_Header, Filing_Rows
#from outside_spending.management.commands.overlay_utils import *

from outside_spending.read_FEC_settings import FILECACHE_DIRECTORY

from form_helpers import process_F24, process_F3X, process_F3X_contribs, process_file

#from dateutil.parser import parse as dateparse

class Command(BaseCommand):
    
    def __init__(self):
        self.fp = form_parser()

    def handle(self, *args, **options):
        """ Run through all the old .fec files and process 'em"""
        


        print "Getting files"
        filecount = 0
        filenums = []
        
        for d, _, files in os.walk(FILECACHE_DIRECTORY):
            for a in files:

                filecount += 1
                filingnum = a.replace(".fec", "")

                #print "%s: Found filing: %s" % (filecount, filingnum)
                #if (int(filingnum)>785500):
                filenums.append(filingnum)
                #print "%s: Found filing: %s" % (filecount, filingnum)

        # make sure we process them in order !!
        filenums.sort()
        
        #filenums = [766892, 762315]

        print "Processing files"
        for filingnum in filenums:
            print "processing %s" % (filingnum)
            process_file(filingnum, self.fp)
            

