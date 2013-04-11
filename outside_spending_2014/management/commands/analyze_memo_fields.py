# Back ref transaction ids are very rarely included. That makes it really hard to compare the 'memo-ized' version of the contribs to the unmemoized. Maybe this stuff is coming from the conduit field instead? We've left that off... 



from django.core.management.base import BaseCommand
from dateutil.parser import parse as dateparse

from outside_spending.models import Expenditure, Contribution

class Command(BaseCommand):
    def handle(self, *args, **options):
        all_x_contribs = Contribution.objects.filter(memo_agg_item__icontains='x')
        for x in all_x_contribs:
            print "Hiding X-ed memo field contrib: '%s' - '%s' - '%s' - '%s' - '%s' - '%s'  - '%s' - '%s' - '%s' - '%s' - '%s'" % (x.line_type, x.filing_number, x.fec_committeeid, x.transaction_id, x.contrib_last, x.contrib_first, x.contrib_date, x.contrib_amt, x.contrib_purpose, x.memo_agg_item, x.memo_text_descript)
            
            
            print "back_ref_tran_id: %s, back_ref_sked_name:%s \n\n" % (x.back_ref_tran_id, x.back_ref_sked_name)
            #x.superceded_by_amendment=True
            #x.save()
 
        all_x_expends = Expenditure.objects.filter(memo_code__icontains='x')
        for x in all_x_expends:
            print "Hiding X-ed memo field expenditure: '%s' - '%s' - '%s' - '%s' - '%s' - '%s'  - '%s'" % (x.filing_number, x.raw_committee_id, x.payee, x.expenditure_amount, x.expenditure_purpose, x.memo_code, x.memo_text_description)
            
            #print "back_ref_tran_id: %s, back_ref_sked_name:%s \n\n" % (x.back_ref_tran_id, x.back_ref_sked_name)
            #x.superceded_by_amendment=True
            #x.save()  
          