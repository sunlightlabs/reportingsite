"""Enter data from forms 24, 5 and 9 from the archive"""

import re
import os

from django.core.management.base import BaseCommand

from outside_spending.form_parser import form_parser
from outside_spending.filing import filing
from outside_spending.models import Filing_Header, Filing_Rows
from outside_spending.management.commands.overlay_utils import *

from outside_spending.outside_spending_settings import filecache_directory, cycle

class Command(BaseCommand):
    
    def __init__(self):
        self.fp = form_parser()
        
    
    
    def process_file(self, filingnum):
        f1 = filing(filingnum)
        f1.download()
        form = f1.get_form_type()
        version = f1.get_version()
        headers = f1.get_headers()
        is_amendment = headers['is_amendment']
        original=None
        filer_id = headers['fec_id']
        if (is_amendment):
            original=headers['filing_amended']
        
        
        if (re.match('^F5', form) or re.match('^F24', form) or re.match('^F9', form) and form!='F99'):
            
             
            #print "Filing: %s filer: %s form:%s version:%s is_amendment:%s original: %s" % (filingnum, filer_id, form, version, is_amendment, original)
            
            
            # form 5's come in a few different flavors. 
            
            if (re.match('^F5', form)):
                parsed_line = self.fp.parse_form_line(f1.get_first_row(), version)
                print "\n***%s:  %s - %s\n %s - %s" % (filingnum, parsed_line['report_code'], parsed_line['report_type'],  parsed_line['coverage_from_date'],  parsed_line['coverage_through_date'])
                if (parsed_line['report_type']!='24' and parsed_line['report_type']!='48'):
                    # ignore reports that aren't 24 or 48
                    print "Missing !!!!"
                    return
            
            
            # it's a form we care about. Create the header row as a django object.
            
            # Get or create the committee overlay. 
            committee_overlay = get_or_create_committee_overlay(filer_id, cycle)
            filing_number = int(filingnum)
            fh=None
            try:
                fh =Filing_Header.objects.get(filing_number=filing_number)
            except Filing_Header.DoesNotExist:
                fh = Filing_Header.objects.create(
                    raw_filer_id=filer_id,
                    form=form,
                    filing_number=filing_number,
                    is_amendment=is_amendment,
                    amends_filing=original,
                    header_text=f1.get_raw_first_row(),
                    filer=committee_overlay
                )
            
            
            
            
            # lines we care about:
            # We're not really doing anything with F91, but it looks interesting
            line_types = ['SE', 'F91','F93', 'F94', 'F57']
            
            for lt in line_types:
                these_rows = f1.get_raw_rows(lt)
                for row_to_enter in these_rows:
                    #print "Processing line: %s" % row_to_enter
                    
                    # We gotta parse the line here to pull the transaction id. Doh. 
                    parsed_line = self.fp.parse_raw_form_line(row_to_enter, version)
                    
                    # NYT's csv files have an inconsistent naming convention... 
                    try:
                        transaction_id = parsed_line['transaction_id']
                    except KeyError:
                        transaction_id = parsed_line['transaction_id_number']
            
                    try:
                        fr = Filing_Rows.objects.get(filing_number=filing_number, transaction_id=transaction_id)
                    except Filing_Rows.DoesNotExist:
                        # create it: 
                        print "Trying to create %s - %s" % (filing_number,transaction_id)
                        fr = Filing_Rows.objects.create(
                            parent_filing=fh,
                            filer=committee_overlay,
                            filing_number=filing_number,
                            parent_form=form,
                            line_type=lt,
                            line_text=row_to_enter,
                            transaction_id=transaction_id)
                        
            
    

    def handle(self, *args, **options):
        """ Run through all the old .fec files and process 'em"""
        
        filecount = 0
        for d, _, files in os.walk(filecache_directory):
            for a in files:

                filecount += 1
                filingnum = a.replace(".fec", "")
                #print "%s: Found filing: %s" % (filecount, filingnum)
                #if (int(filingnum)>767015):
                
                #print "%s: Found filing: %s" % (filecount, filingnum)
                self.process_file(filingnum)
                    