import urllib
import urllib2
import re
from dateutil.parser import parse as dateparse


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from rebuckley.models import *

from enter_f3x import enter_form

def process_committee_page(pagehtml, committee_id):

    form_3x_regex = re.compile(r'<DT><A HREF=\'\d+\/\'>Form F3X[N|A]\s*-\s*(.*?\s*</A>\s*.+?Filed \d+\/\d+\/\d+)', re.DOTALL)
    form_3x_match = re.compile(r'(\d+\/\d+\/\d+)</A>\s*\n<DD>FEC Filing #: FEC-(\d\d\d\d\d\d)\s*\n<DD>Period FROM (\d+\/\d+\/\d+) through (\d+\/\d+\/\d+)\s*\n<DD> Report Type: (.*?)\n' )

    form_3fxs =  re.findall(form_3x_regex, pagehtml)
    for f in form_3fxs:
        #print "\n\n***" + f 
        t = re.match(form_3x_match, f)
        if t:
            file_date = t.group(1)
            file_id = t.group(2)
            period_start = t.group(3)
            period_end = t.group(4)
            report_type = t.group(5)

            print "-->F3X filed on %s %s for %s-%s\nhttp://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/\n\n" % (file_date, report_type, period_start, period_end, committee_id, file_id)
            dl_url = 'http://query.nictusa.com/dcdev/posted/%s.fec' % (file_id)
            if dateparse(period_end)>dateparse('1/1/2011'):

                print "Processing filing: %s, dl_url: %s" % (file_id, dl_url)
                this_page = urllib2.urlopen(dl_url).read()
                enter_form(this_page, file_id)

        else:
            print "\n\n\n*****no match\n\n\n"

class Command(BaseCommand):
    help = "Watches for new superpac F3X[N|A] (contrib) reports"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        #all_superpacs = IEOnlyCommittee.objects.all().filter(total_presidential_indy_expenditures__gte=100)
        all_superpacs = IEOnlyCommittee.objects.all()
        for sp in all_superpacs:
            
            print "%s - %s" % (sp.fec_name, sp.fec_id)
            url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/" % (sp.fec_id)
            html = urllib.urlopen(url)
            response = html.read()
            process_committee_page(response, sp.fec_id)

        