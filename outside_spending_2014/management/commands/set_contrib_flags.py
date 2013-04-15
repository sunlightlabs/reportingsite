## ASSUMES THAT THE 3FX's have already been pruned and the contribs purged !! 

# updated to automatically pick the most recent 3FX filing and use that for cash on hand etc. 

# need a separate script to set cash on hand for filngs that land at the end of last cycle. Will handle separately. 

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Count
from dateutil.parser import parse as dateparse
from outside_spending_2014.models import *
from outside_spending_2014.read_FEC_settings import CYCLE, CYCLE_START, CYCLE_END, LAST_CYCLE_END

epoch_start = dateparse(CYCLE_START)


class Command(BaseCommand):
    help = "Set superpac fields"
    requires_model_validation = False
    
    def handle(self, *args, **options):

        # calc superpac totals
        all_superpacs = Committee_Overlay.objects.filter(cycle=CYCLE, is_superpac=True)
        for sp in all_superpacs:
            try:
                
                f3s = F3X_Summary.objects.filter(coverage_from_date__gte=epoch_start, fec_id=sp.fec_id).filter(superceded_by_amendment=False).order_by('-coverage_to_date')
                f3 = f3s[0]
                
                total_contributions = f3s.aggregate(receipts=Sum('total_receipts'), tot_unitemized=Sum('unitemized'))

                
                
                
                total = total_contributions['receipts']
                total_unitemized = total_contributions['tot_unitemized']
                
                print "%s total receipts = %s, unitemized=%s" % (sp.name, total_contributions['receipts'], total_unitemized)
                
                
                sp.total_contributions = total
                sp.total_unitemized = total_unitemized
                sp.cash_on_hand=f3.coh_close
                sp.cash_on_hand_date = f3.coverage_to_date
                

        
            except IndexError:
                
                pass

            
            num_contributions = Contribution.objects.filter(fec_committeeid=sp.fec_id, superceded_by_amendment=False,contrib_date__gte=epoch_start).aggregate(num=Count('fec_committeeid'))
            if (num_contributions['num']>0):
                sp.has_contributions=True
            else:
                sp.has_contributions=False
            
            sp.save()
        
