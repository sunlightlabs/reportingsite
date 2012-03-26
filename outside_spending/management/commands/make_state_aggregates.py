import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from django.contrib.localflavor.us.us_states import STATE_CHOICES


from outside_spending.models import *



today = datetime.date.today()
two_weeks_ago = today - datetime.timedelta(days=14)

STATE_CHOICES = dict(STATE_CHOICES)

class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        
        for state in STATE_CHOICES:
            
            
            # is there any spending at all ? 
            
            total_ind_exp = Expenditure.objects.filter(superceded_by_amendment=False, state=state).aggregate(total=Sum('expenditure_amount'))
            
            
            
            if total_ind_exp['total'] > 0:
                
                recent_ind_exp = Expenditure.objects.filter(superceded_by_amendment=False, state=state, expenditure_date__gte=two_weeks_ago).aggregate(total=Sum('expenditure_amount'))
                recent_pres_exp = Expenditure.objects.filter(superceded_by_amendment=False, state=state, expenditure_date__gte=two_weeks_ago, office='P').aggregate(total=Sum('expenditure_amount'))
                
                print "State: %s total %s recent %s" % (state, total_ind_exp['total'], recent_ind_exp['total'])
            
                # pres:
                tps = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='P', state=state, support_oppose__iexact='S').aggregate(total=Sum('expenditure_amount'))
                tpo = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='P', state=state, support_oppose__iexact='O').aggregate(total=Sum('expenditure_amount'))
                tp = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='P', state=state).aggregate(total=Sum('expenditure_amount'))
            
                # house 
                ths = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='H', state=state, support_oppose__iexact='S').aggregate(total=Sum('expenditure_amount'))
                tho = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='H', state=state, support_oppose__iexact='O').aggregate(total=Sum('expenditure_amount'))
                th = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='H', state=state).aggregate(total=Sum('expenditure_amount'))
            
                # senate
                tss = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='S', state=state, support_oppose__iexact='S').aggregate(total=Sum('expenditure_amount'))
                tso = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='S', state=state, support_oppose__iexact='O').aggregate(total=Sum('expenditure_amount'))
                ts = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office='S', state=state).aggregate(total=Sum('expenditure_amount'))
                
                # ec
                ec = Electioneering_93.objects.filter(superceded_by_amendment=False, target__candidate__state_race=state).distinct().aggregate(total=Sum('exp_amo'))
                print ec
            
            
            
                
                this_state, created = State_Aggregate.objects.get_or_create(state=state)

                this_state.expenditures_supporting_president = tps['total']
                this_state.expenditures_opposing_president = tpo['total']
                this_state.total_pres_ind_exp = tp['total']
                this_state.expenditures_supporting_house = ths['total']
                this_state.expenditures_opposing_house = ths['total']
                this_state.total_house_ind_exp = th['total']
                this_state.expenditures_supporting_senate = tss['total']
                this_state.expenditures_opposing_senate = tso['total']
                this_state.total_senate_ind_exp = ts['total']     
                this_state.total_ind_exp = total_ind_exp['total']
                this_state.recent_ind_exp = recent_ind_exp['total']
                this_state.recent_pres_exp =recent_pres_exp['total']
                this_state.total_ec=ec['total']
                this_state.save()
                    
                    
                    
