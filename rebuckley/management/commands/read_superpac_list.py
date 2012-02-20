import urllib2
import socket
import re

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from rebuckley.models import IEOnlyCommittee, Committee


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
            
            # set the superpac flag for these committees:
            try: 
                committee = Committee.objects.get(fec_id=committee_id)
                committee.is_superpac=True
                committee.save()
            except Committee.DoesNotExist:
                pass
            
            
            try:
                sp = IEOnlyCommittee.objects.get(fec_id=committee_id)
                # They're constantly changing their filing dates, so upatethese... 
                sp.filing_freq_verbatim=filing_freq
                sp.save()
            except IEOnlyCommittee.DoesNotExist:
                print "saving: %s" % (name)
                ieoc = IEOnlyCommittee.objects.create(
                    fec_id=committee_id,
                    fec_name=name,
                    slug=slugify(name)[0:50],
                    filing_freq_verbatim=filing_freq
                )
                ieoc.save()
            
            
                
            # Super pac listings use a newer name than what's in the committee master, so locate the original record and sync the name. This is a sorta dumb circumstance, but... 
            try: 
                com = Committee.objects.get(fec_id=committee_id)
                com.name = name
                com.save()
            except Committee.DoesNotExist:
                print "*** Can't find original record for %s %s" % (committee_id, name)
            
            