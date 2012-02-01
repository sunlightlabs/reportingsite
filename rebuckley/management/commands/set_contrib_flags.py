from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Count
from dateutil.parser import parse as dateparse
from rebuckley.models import *

class Command(BaseCommand):
    help = "Set superpac fields"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        cash_on_hand_date = dateparse('2011-12-31')
        # calc superpac totals
        all_superpacs = IEOnlyCommittee.objects.all()
        for sp in all_superpacs:
            try:
                has_contrib = 0
                f3s = F3X_Summary.objects.filter(fec_id=sp.fec_id).filter(coverage_to_date=cash_on_hand_date).order_by('-filing_number')
                f3 = f3s[0]
                
                
                sp.cash_on_hand=f3.coh_close

        
            except IndexError:
                sp.cash_on_hand=None
            
                
            total_contributions = Contribution.objects.filter(fec_committeeid=sp.fec_id).filter(contrib_date__gte='2011-01-01').aggregate(total_spent=Sum('contrib_amt'))
            sp.total_contributions = total_contributions['total_spent']
            num_contributions = Contribution.objects.filter(fec_committeeid=sp.fec_id).filter(contrib_date__gte='2011-01-01').aggregate(num=Count('fec_committeeid'))
            if (num_contributions['num']>0):
                sp.has_contributions=True
            else:
                sp.has_contributions=False
            
            sp.save()
        
        