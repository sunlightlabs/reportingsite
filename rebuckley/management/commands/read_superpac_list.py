import urllib2
import socket
import re

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from rebuckley.models import IEOnlyCommittee


socket.setdefaulttimeout(10000)

class Command(BaseCommand):

    def handle(self, *args, **options):
        url = 'http://www.fec.gov/press/press2011/ieoc_alpha.shtml'
        page = urllib2.urlopen(url).read()
        
        linere = re.compile(r'(<tr BGCOLOR="#F[F5]F[F0]FF">\s*<td scope="row">\d+</td>\s*<td>\w\d+</td><td><a href="http://images.nictusa.com/cgi-bin/fecimg/\?\w\d+">.*?</a></td><td>.*?</td></tr>)')

        linere2= re.compile(r'(<tr BGCOLOR="#F[F5]F[F0]FF">\s*<td scope="row">\d+</td>\s*<td>(\w\d+)</td><td><a href="http://images.nictusa.com/cgi-bin/fecimg/\?\w\d+">(.*?)</a></td><td>(.*?)</td></tr>)')
        
        rows = re.findall(linere, page)
        count = 0
        for a in rows:
            m = re.search(linere2, a)
            committee_id = m.group(2)
            name = m.group(3)
            filing_freq = m.group(4) 
            
            try:
                IEOnlyCommittee.objects.get(fec_id=committee_id)
            except IEOnlyCommittee.DoesNotExist:
                print "saving: %s" % (name)
                ieoc = IEOnlyCommittee.objects.create(
                    fec_id=committee_id,
                    fec_name=name,
                    slug=slugify(name)[0:50],
                    filing_freq_verbatim=filing_freq
                )
                ieoc.save()
            
            