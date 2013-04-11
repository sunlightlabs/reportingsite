


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending_2014.models import *

from outside_spending_2014.read_FEC_settings import CYCLE, CYCLE_START, CYCLE_END

class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False


    def handle(self, *args, **options):
        # Set IE flags
        candidate_ids = Expenditure.objects.filter(superceded_by_amendment=False, cycle=CYCLE).values('candidate__fec_id').distinct().order_by()
        for candidate_id in candidate_ids:
            # ignore nulls
            if (candidate_id['candidate__fec_id']):
                print "Looking for %s" % candidate_id
                candidate = Candidate_Overlay.objects.get(cycle=CYCLE, fec_id=candidate_id['candidate__fec_id'])
                total_supporting = Expenditure.objects.filter(cycle=CYCLE, superceded_by_amendment=False, candidate=candidate, support_oppose__iexact='S').aggregate(total=Sum('expenditure_amount'))
                total_opposing = Expenditure.objects.filter(cycle=CYCLE, superceded_by_amendment=False, candidate=candidate, support_oppose__iexact='O').aggregate(total=Sum('expenditure_amount'))
                total = Expenditure.objects.filter(cycle=CYCLE, superceded_by_amendment=False, candidate=candidate).aggregate(total=Sum('expenditure_amount'))
            
                print "%s : %s %s %s" % (candidate.fec_name, total_supporting['total'], total_opposing['total'], total['total'])
                
                
                    
                candidate.expenditures_supporting = total_supporting['total']
                candidate.expenditures_opposing = total_opposing['total']
                candidate.total_expenditures = total['total']
                candidate.save()
        
        # set EC totals
        candidate_ids = Electioneering_94.objects.filter(cycle=CYCLE, superceded_by_amendment=False).values('candidate__fec_id').distinct()
        for candidate_id in candidate_ids: 
            this_id = candidate_id['candidate__fec_id']
            # skip missing values
            if this_id:
                print "Got id: %s" % (this_id)
                total = Electioneering_93.objects.filter(cycle=CYCLE, superceded_by_amendment=False, target__candidate__fec_id=this_id).distinct().aggregate(total=Sum('exp_amo'))
                candidate = Candidate_Overlay.objects.get(cycle=CYCLE, fec_id=this_id)
                candidate.electioneering=total['total']
                candidate.save()

        

              