import urllib
import urllib2
import re
from dateutil.parser import parse as dateparse


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from rebuckley.models import *

from enter_f3x import enter_form

def get_total(fec_file):

    filing_dir = "/Users/jfenton/reporting/reportingsite/rebuckley/data/filings/3fx/2011/"

    thisfile = filing_dir + str(fec_file) + ".fec"

    local_file = open(thisfile, 'r')

    # The new FCC files are delimited by ascii 28 
    delimiter = chr(28)

    line_num = 0
    yearly_total = 0
    for line in local_file:
        line_num += 1
    # kill off the new lines 
        line = line.replace("\n","") 
        line = line.replace("\r","")

        fields = line.split(delimiter)
        if line_num == 2:
            #print "Got filing num: '%s' " % (fields[0])

            print "name: %s id: %s start: %s end: %s cash on hand close: %s total receipts (period):%s total receipts (ytd) %s loans: %s" % (fields[2], fields[1], fields[13], fields[14], fields[26], fields[23], fields[75], fields[86])
            yearly_total = float(fields[77]) + float(fields[102])
            return yearly_total



class Command(BaseCommand):
    help = "Watches for new superpac F3X[N|A] (contrib) reports"
    requires_model_validation = False


    def handle(self, *args, **options):
        reports = F3X_Summary.objects.filter(coverage_to_date='2011-12-31')
        running_total = 0
        
        linetypehash = {}
        # The new FCC files are delimited by ascii 28 
        delimiter = chr(28)

        
        for report in reports:
            file_to_process = report.filing_number
            
            filing_dir = "/Users/jfenton/reporting/reportingsite/rebuckley/data/filings/3fx/2011/"

            thisfile = filing_dir + str(file_to_process) + ".fec"

            local_file = open(thisfile, 'r')
 

            linecount = 0
            yearly_total = 0
            for line in local_file:
                linecount += 1
            # kill off the new lines 
                line = line.replace("\n","") 
                line = line.replace("\r","")

                fields = line.split(delimiter)
                
                line_type = fields[0].upper()
                
                if (linecount==1): 
                        #print "'header line': %s" % fields
                        #print "Verifying header version" 
                        assert (fields[2].strip()=="8.0")            

                if (linecount==2):
                    pass           

                if (linecount > 2):
                    try:
                        count = linetypehash[line_type]
                    except KeyError:
                        count = 0
                    linetypehash[line_type]= count+1


        print "Summarizing data lines"            
        for k in linetypehash:
            print "%s - %s" % (k, linetypehash[k])                                    