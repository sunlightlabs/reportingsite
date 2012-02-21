## ASSUMES THAT THE 3FX's have already been pruned and the contribs purged !! 

# updated to automatically pick the most recent 3FX filing and use that for cash on hand etc. 

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Count
from dateutil.parser import parse as dateparse
from rebuckley.models import *

class Command(BaseCommand):
    help = "Set superpac fields"
    requires_model_validation = False
    
    def handle(self, *args, **options):

        # calc superpac totals
        all_superpacs = IEOnlyCommittee.objects.all()
        for sp in all_superpacs:
            try:
                
                f3s = F3X_Summary.objects.filter(fec_id=sp.fec_id).order_by('-filing_number')
                f3 = f3s[0]
                
                total_contributions = f3s.aggregate(receipts=Sum('total_receipts'))
                operating_expenses_offsets = Contribution.objects.filter(superpac__fec_id=sp.fec_id, superceded_by_amendment=False, line_type='SA15').aggregate(total_contribs=Sum('contrib_amt'))
                
                total = 0
                if operating_expenses_offsets['total_contribs']:
                    total = total_contributions['receipts'] + operating_expenses_offsets['total_contribs']
                else:
                    total = total_contributions['receipts']

                print "SA15 spending %s offsets: %s other total: %s" % (sp.fec_name, operating_expenses_offsets['total_contribs'], total_contributions['receipts'])
                
                
                sp.total_contributions = total
                sp.cash_on_hand=f3.coh_close
                sp.cash_on_hand_date = f3.coverage_to_date
                

        
            except IndexError:
                sp.cash_on_hand=None
            

            
            num_contributions = Contribution.objects.filter(fec_committeeid=sp.fec_id).filter(contrib_date__gte='2011-01-01').aggregate(num=Count('fec_committeeid'))
            if (num_contributions['num']>0):
                sp.has_contributions=True
            else:
                sp.has_contributions=False
            
            sp.save()
        
