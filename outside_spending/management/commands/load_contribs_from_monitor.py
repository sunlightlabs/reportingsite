import urllib
import urllib2
import re
import time

import socket

from dateutil.parser import parse as dateparse


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending.models import *

from outside_spending.utils.fec_logging import fec_logger

from enter_f3x import enter_form

# Give 'em 15 seconds to respond. 
socket.setdefaulttimeout(15000)
my_logger=fec_logger()


def download_with_headers(url):
    headers = { 'User-Agent' : "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)" }    
    req = urllib2.Request(url, None, headers)
    page_read = urllib2.urlopen(req).read()
    return page_read


class Command(BaseCommand):
    help = "Watches for new superpac F3X[N|A] (contrib) reports"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        #all_superpacs = IEOnlyCommittee.objects.all().filter(total_presidential_indy_expenditures__gte=100)
        #all_superpacs = IEOnlyCommittee.objects.all()
        all_superpacs = Committee_Overlay.objects.filter(filing_frequency__iexact='M', is_superpac=True)
        for sp in all_superpacs:
            
            try:
                current_filing = F3X_Summary.objects.get(fec_id=sp.fec_id, coverage_to_date='2012-04-30')
                print "Found Mar monthly filing from: %s" % (sp.name)
                continue
                            
            except: 
                #print "Looking for filings from: %s" % (sp.name)
            
                # look for filings in the unprocess_filings model
                f = None
                try:
                    f = unprocessed_filing.objects.get(form_type='F3XN', fec_id=sp.fec_id, coverage_to_date__in=['2012-04-30', '2012-05-02', '2012-05-09'])
                except:
                    continue
                
                
                print "%s %s %s" % (f.committee_name, f.filing_number, f.coverage_to_date)
                
                dl_url = 'http://query.nictusa.com/dcdev/posted/%s.fec' % (f.filing_number)
                print "\t===+Processing filing: %s, dl_url: %s" % (f.filing_number, dl_url)
                my_logger.info('LOAD_CONTRIBS_FROM_MONITOR - loading file %s' % f.filing_number)
                this_page = download_with_headers(dl_url)
                time.sleep(3)
                enter_form(this_page, f.filing_number)
            