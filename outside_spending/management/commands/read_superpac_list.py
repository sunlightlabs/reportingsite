import urllib2
import socket
import re

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from outside_spending.models import Committee_Overlay
from outside_spending.management.commands.overlay_utils import *


socket.setdefaulttimeout(10000)
# change this in 2014... 
cycle = 2012

class Command(BaseCommand):

    def handle(self, *args, **options):
        url = 'http://www.fec.gov/press/press2011/ieoc_alpha.shtml'
        page = urllib2.urlopen(url).read()
        
        linere = re.compile(r'(<tr BGCOLOR="#F[F5]F[F0]FF">\s*<td scope="row">\d+</td>\s*<td>\w\d+</td><td><a href="http://images.nictusa.com/cgi-bin/fecimg/\?\w\d+">.*?</a></td><td>.*?</td></tr>)')

        linere2= re.compile(r'(<tr BGCOLOR="#F[F5]F[F0]FF">\s*<td scope="row">\d+</td>\s*<td>(\w\d+)</td><td><a href="http://images.nictusa.com/cgi-bin/fecimg/\?\w\d+">(.*?)</a></td><td>(.*?)</td></tr>)')
        
        rows = re.findall(linere, page)

        for a in rows:
            m = re.search(linere2, a)
            committee_id = m.group(2)
            name = m.group(3)
            filing_freq = m.group(4) 
            filing_freq_abbrev = ""
            
            if (re.match('.*MONTHLY FILER.*', filing_freq, re.I)):
                filing_freq_abbrev = 'M'
            elif(re.match('.*QUARTERLY FILER.*', filing_freq, re.I)):
                filing_freq_abbrev = 'Q'
            elif(re.match('.*DEBT.*', filing_freq, re.I)):
                filing_freq_abbrev = 'D'
            elif(re.match('.*ADMINISTRATIVELY TERMINATED.*', filing_freq, re.I)):
                filing_freq_abbrev = 'A'
            elif(re.match('.*TERMINATED.*', filing_freq, re.I)):
                filing_freq_abbrev = 'T'
            elif(re.match('.*WAIVED.*', filing_freq, re.I)):
                filing_freq_abbrev = 'W'                                                
                            
            superpac = get_or_create_committee_overlay(committee_id, cycle)
            
            # 
            if (superpac):
                #print "Processing superpac: %s" % (superpac)
                if (not superpac.is_superpac):
                    superpac.is_superpac = True
                    superpac.save()
            
            else:            
                print "Couldn't create superpac from existing record: %s" % (name)
                superpac = Committee_Overlay.objects.create(
                    fec_id=committee_id,
                    cycle=cycle,
                    name=name,
                    slug=slugify(name)[0:50],
                    filing_frequency=filing_freq_abbrev,
                    is_superpac = True
                )
                
            
            