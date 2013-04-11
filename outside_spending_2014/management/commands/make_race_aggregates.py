


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending_2014.models import *
from outside_spending_2014.read_FEC_settings import CYCLE, CYCLE_START, CYCLE_END


class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        # District is '00' for Senate, President. This is pretty clean since we're pulling the candidate id--but maybe more caution is warranted. 
        # In old raw filings, allegedly some spending targeted Obama's old account. 
        races = Expenditure.objects.filter(superceded_by_amendment=False, cycle=CYCLE).values('candidate__office', 'candidate__state_race', 'candidate__district').distinct().order_by()
        
        for r in races:
            print "handling %s %s %s" %  (r['candidate__office'], r['candidate__state_race'], r['candidate__district'])
            total_supporting = Expenditure.objects.filter(cycle=CYCLE, superceded_by_amendment=False, candidate__office=r['candidate__office'], candidate__state_race=r['candidate__state_race'], candidate__district=r['candidate__district'], support_oppose__iexact='S').aggregate(total=Sum('expenditure_amount'))
            total_opposing = Expenditure.objects.filter(cycle=CYCLE, superceded_by_amendment=False, candidate__office=r['candidate__office'], candidate__state_race=r['candidate__state_race'], candidate__district=r['candidate__district'], support_oppose__iexact='O').aggregate(total=Sum('expenditure_amount'))
            total = Expenditure.objects.filter(cycle=CYCLE, superceded_by_amendment=False, candidate__office=r['candidate__office'], candidate__state_race=r['candidate__state_race'], candidate__district=r['candidate__district']).aggregate(total=Sum('expenditure_amount'))
            
            total_ec = None
            # Now handle EC stuff: 
            if (r['candidate__office']=='P'):
                total_ec = Electioneering_93.objects.filter(cycle=CYCLE, superceded_by_amendment=False, target__candidate__office=r['candidate__office']).distinct().aggregate(total=Sum('exp_amo'))
            else:
                total_ec = Electioneering_93.objects.filter(cycle=CYCLE, superceded_by_amendment=False, target__candidate__office=r['candidate__office'], target__candidate__district=r['candidate__district'], target__can_state=r['candidate__state_race']).distinct().aggregate(total=Sum('exp_amo'))
            
            print "** electioneering: %s" % (total_ec)
            
            
            try:
                aggregate = Race_Aggregate.objects.get(cycle=CYCLE, office=r['candidate__office'], state=r['candidate__state_race'], district=r['candidate__district'])
                aggregate.expenditures_supporting = total_supporting['total']
                aggregate.expenditures_opposing = total_opposing['total']
                aggregate.total_ind_exp = total['total'] 
                aggregate.total_ec = total_ec['total'] 
                aggregate.save()
            except Race_Aggregate.DoesNotExist:
                aggregate = Race_Aggregate.objects.create(
                    cycle=CYCLE,
                    office=r['candidate__office'], 
                    state=r['candidate__state_race'], 
                    district=r['candidate__district'],
                    expenditures_opposing = total_opposing['total'],
                    expenditures_supporting = total_supporting['total'],
                    total_ind_exp = total['total'],
                    total_ec = total_ec['total']
                )                                
                aggregate.save()
                
            print "total is %s, %s, %s" % (total_supporting['total'], total_opposing['total'], total['total'])
            
            
            
            
                    