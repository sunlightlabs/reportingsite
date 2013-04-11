# Mark stuff with an x in the memo field as if it's been amended. 
# There tend to be problems with this stuff on the original reports, but there's not much we can 
# do about it. 



from django.core.management.base import BaseCommand
from dateutil.parser import parse as dateparse

from outside_spending_2014.models import Expenditure, Contribution
from outside_spending_2014.read_FEC_settings import CYCLE, CYCLE_START, CYCLE_END

cycle_start_date = dateparse(CYCLE_START)
cycle_end_date = dateparse(CYCLE_END)


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_x_contribs = Contribution.objects.filter(memo_agg_item__icontains='x', superceded_by_amendment=False, contrib_date__gte=cycle_start_date, contrib_date__lte=cycle_end_date)
        for x in all_x_contribs:
            print "Hiding X-ed memo field contrib: '%s' - '%s' - '%s' - '%s' - '%s' - '%s'  - '%s' - '%s' - '%s' - '%s' - '%s'" % (x.line_type, x.filing_number, x.fec_committeeid, x.transaction_id, x.contrib_last, x.contrib_first, x.contrib_date, x.contrib_amt, x.contrib_purpose, x.memo_agg_item, x.memo_text_descript)
            
            x.superceded_by_amendment=True
            x.save()

        all_x_expends = Expenditure.objects.filter(memo_code__icontains='x', superceded_by_amendment=False,expenditure_date__gte=cycle_start_date, expenditure_date__lte=cycle_end_date)
        for x in all_x_expends:
            print "Hiding X-ed memo field expenditure: '%s' - '%s' - '%s' - '%s' - '%s' - '%s'  - '%s'" % (x.filing_number, x.raw_committee_id, x.payee, x.expenditure_amount, x.expenditure_purpose, x.memo_code, x.memo_text_description)
            x.superceded_by_amendment=True
            x.save()            