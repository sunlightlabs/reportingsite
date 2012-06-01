# Mark stuff with an x in the memo field as if it's been amended. This is bad practice, but... 



from django.core.management.base import BaseCommand
from dateutil.parser import parse as dateparse

from outside_spending.models import Expenditure, Contribution

class Command(BaseCommand):
    def handle(self, *args, **options):
        all_x_contribs = Contribution.objects.filter(memo_agg_item__icontains='x', superceded_by_amendment=False)
        for x in all_x_contribs:
            print "Hiding X-ed memo field contrib: '%s' - '%s' - '%s' - '%s' - '%s' - '%s'  - '%s' - '%s' - '%s' - '%s' - '%s'" % (x.line_type, x.filing_number, x.fec_committeeid, x.transaction_id, x.contrib_last, x.contrib_first, x.contrib_date, x.contrib_amt, x.contrib_purpose, x.memo_agg_item, x.memo_text_descript)
            x.superceded_by_amendment=True
            x.save()

        all_x_expends = Expenditure.objects.filter(memo_code__icontains='x', superceded_by_amendment=False)
        for x in all_x_expends:
            print "Hiding X-ed memo field expenditure: '%s' - '%s' - '%s' - '%s' - '%s' - '%s'  - '%s'" % (x.filing_number, x.raw_committee_id, x.payee, x.expenditure_amount, x.expenditure_purpose, x.memo_code, x.memo_text_descript)
            x.superceded_by_amendment=True
            x.save()            