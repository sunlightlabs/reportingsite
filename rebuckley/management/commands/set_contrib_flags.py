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
                f3 = F3X_Summary.objects.filter(fec_id=sp.fec_id).order_by('-filing_number')[0]
                sp.total_contributions = f3.total_receipts
                sp.cash_on_hand=f3.coh_close
                sp.cash_on_hand_date=f3.coverage_to_date
                if (f3.itemized):
                    sp.has_contributions=True
        
            except IndexError:
                sp.total_contributions = 0
                sp.has_contributions=False
            
            sp.save()
        
        