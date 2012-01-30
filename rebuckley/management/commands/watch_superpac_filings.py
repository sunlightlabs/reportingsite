import urllib
import re


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from rebuckley.models import *

class Command(BaseCommand):
    help = "Watches for new superpac F3X[N|A] (contrib) reports"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        fec_id_regex = re.compile(r'[0-9]{6}')
        all_superpacs = IEOnlyCommittee.objects.all().filter(total_presidential_indy_expenditures__gte=100)
        for sp in all_superpacs:
            
            print "looknig for filings from: %s - %s" % (sp.fec_name, sp.fec_id)
            url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/" % (sp.fec_id)
            html = urllib.urlopen(url)
            response = html.read()

            for line in response.splitlines():
                    if re.search("Form F3XN", line) and re.search(fec_id_regex, line):
                        this_report =  re.findall(fec_id_regex, line)
                        if (int(this_report[0])>750000):
                            print "Got original F3X filing: http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/" % (sp.fec_id, this_report[0])

                    if re.search("Form F3XA", line) and re.search(fec_id_regex, line):
                        this_report =  re.findall(fec_id_regex, line)
                        if (int(this_report[0])>750000):
                            print "Got original F3X filing: http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/" % (sp.fec_id, this_report[0])


            