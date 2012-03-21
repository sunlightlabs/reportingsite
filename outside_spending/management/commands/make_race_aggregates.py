


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending.models import *

class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        # District is '00' for Senate, President. This is pretty clean since we're pulling the candidate id--but maybe more caution is warranted. 
        # In old raw filings, allegedly some spending targeted Obama's old account. 
        races = Expenditure.objects.filter(superceded_by_amendment=False).values('candidate__office', 'candidate__state_race', 'candidate__district').distinct().order_by()
        
        for r in races:
            print "handling %s %s %s" %  (r['candidate__office'], r['candidate__state_race'], r['candidate__district'])
            total_supporting = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office=r['candidate__office'], candidate__state_race=r['candidate__state_race'], candidate__district=r['candidate__district'], support_oppose__iexact='S').aggregate(total=Sum('expenditure_amount'))
            total_opposing = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office=r['candidate__office'], candidate__state_race=r['candidate__state_race'], candidate__district=r['candidate__district'], support_oppose__iexact='O').aggregate(total=Sum('expenditure_amount'))
            total = Expenditure.objects.filter(superceded_by_amendment=False, candidate__office=r['candidate__office'], candidate__state_race=r['candidate__state_race'], candidate__district=r['candidate__district']).aggregate(total=Sum('expenditure_amount'))
            
            try:
                aggregate = Race_Aggregate.objects.get(office=r['candidate__office'], state=r['candidate__state_race'], district=r['candidate__district'])
                aggregate.expenditures_supporting = total_supporting['total']
                aggregate.expenditures_opposing = total_opposing['total']
                aggregate.total_ind_exp = total['total'] 
                aggregate.save()
            except Race_Aggregate.DoesNotExist:
                aggregate = Race_Aggregate.objects.create(
                    office=r['candidate__office'], 
                    state=r['candidate__state_race'], 
                    district=r['candidate__district'],
                    expenditures_opposing = total_opposing['total'],
                    expenditures_supporting = total_supporting['total'],
                    total_ind_exp = total['total']
                )                                
                aggregate.save()
                
            print "total is %s, %s, %s" % (total_supporting['total'], total_opposing['total'], total['total'])
            
            
                    