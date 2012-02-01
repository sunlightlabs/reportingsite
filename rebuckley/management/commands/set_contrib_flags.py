from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from rebuckley.models import *

class Command(BaseCommand):
    help = "Set superpac fields"
    requires_model_validation = False
    
    
    def handle(self, *args, **options):
        # calc superpac totals
        all_superpacs = IEOnlyCommittee.objects.all()
        for sp in all_superpacs:
            try:
                has_contrib = 0
                f3s = F3X_Summary.objects.filter(fec_id=sp.fec_id).order_by('-filing_number')
                f3 = f3s[0]
                
                # As long as one of the cycles we're looking at is itemized we're good. 
                for f in f3s:
                    if (f.itemized):
                        has_contrib+=1
                if has_contrib > 0:
                    sp.has_contributions=True
                
                
                sp.cash_on_hand=f3.coh_close
                sp.cash_on_hand_date=f3.coverage_to_date
        
            except IndexError:
                sp.total_contributions = 0
                sp.has_contributions=False
                
            total_contributions = Contribution.objects.filter(fec_committeeid=sp.fec_id).filter(contrib_date__gte='2011-01-01').aggregate(total_spent=Sum('contrib_amt'))
            sp.total_contributions = total_contributions['total_spent']
            
            sp.save()
        
        