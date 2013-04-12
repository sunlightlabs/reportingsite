 

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Count
from dateutil.parser import parse as dateparse
from outside_spending_2014.models import *
from outside_spending_2014.read_FEC_settings import CYCLE, CYCLE_START, CYCLE_END

epoch_start = dateparse(CYCLE_START)


class Command(BaseCommand):
    help = "Set cash on hand for the 2014 cycle based on the end of the 2012 cycle. Only run this at the beginning of the cycle! It should check before whacking, but... "
    requires_model_validation = False
    
    def handle(self, *args, **options):

        # get superpacs missing cash on hand -- ignore administrativel terminated ones
        all_superpacs = Committee_Overlay.objects.filter(cycle=CYCLE, is_superpac=True, cash_on_hand_date__isnull=True).exclude(committee_master_record__filing_frequency='T')
        
        for i, sp in enumerate(all_superpacs):
            freq = sp.committee_master_record.filing_frequency
            print "%s: got pac:%s and ctype:%s" % (i, sp.name, freq)
            cycle_end = dateparse('2012-12-31')
            try:
                filing = F3X_Summary.objects.get(superceded_by_amendment=False, fec_id=sp.fec_id, coverage_to_date=cycle_end)
                print "Found "
                
                sp.cash_on_hand = filing.coh_close
                sp.cash_on_hand_date = cycle_end
                sp.save()
            except F3X_Summary.DoesNotExist:
                print "missing."
