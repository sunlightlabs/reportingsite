import urllib2
import socket
import re


from django.core.management.base import BaseCommand

from outside_spending.models import Committee_Overlay
from outside_spending.management.commands.overlay_utils import *


socket.setdefaulttimeout(10000)
# change this in 2014... 
cycle = 2012

class Command(BaseCommand):

    def handle(self, *args, **options):
        #url = 'http://www.fec.gov/press/press2011/2012PoliticalCommitteeswithNon-ContributionAccounts.shtml'
        #page = urllib2.urlopen(url).read()
        # the hybrid superpac page seems to be maintained by hand and is basically a disaster. Instead, we're just gonna keep up a list of 'em, right here. Oye. 
        
        hybrid_superpac_list = ['C00401224', 'C00492124', 'C00436873', 'C00001727', 'C00496505', 'C00500033', 'C00500009', 'C00476978', 'C00495275', 'C00493510', 'C00486837', 'C00383182', 'C00359992', 'C00476838', 'C00468447', 'C00509489', 'C00487025', 'C00507053', 'C00461772', 'C00455378', 'C00501262', 'C00501023', 'C00468868']
        for hsp_id in  hybrid_superpac_list:
            hsp = get_or_create_committee_overlay(hsp_id, cycle)
            if (hsp):
                print "Found hybrid super pac: %s" % (hsp)
                hsp.is_hybrid = True
                hsp.save()
            else:
                print "*** Couldn't locate hybrid super pac with id=%s" % (hsp_id)
        