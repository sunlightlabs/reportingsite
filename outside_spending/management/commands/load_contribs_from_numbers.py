""" Hack to add whatever fiilngs have been missed. """
import urllib
import urllib2
import re
import time

import socket

from dateutil.parser import parse as dateparse


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending.models import *

from enter_f3x import enter_form

# Give 'em 15 seconds to respond. 
socket.setdefaulttimeout(15000)


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
        
        # enter some by hand here: 
        filing_numbers = [784874, 784852, 784797, 784649, 784646, 784635, 784610, 784511, 784502, 784247, 783487, 783375, 782563, 782432, 782232, 782000, 781936, 781853, 781632, 781271, 781127, 780966, 780945, 780906, 780628, 780529]
        for filing_number in filing_numbers:
            
            dl_url = 'http://query.nictusa.com/dcdev/posted/%s.fec' % (filing_number)
            print "\t===+Processing filing: %s, dl_url: %s" % (filing_number, dl_url)
            this_page = download_with_headers(dl_url)
            time.sleep(3)
            enter_form(this_page, filing_number)
            