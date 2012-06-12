from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending.models import *

class Command(BaseCommand):
    help = "Sums superpac stuff"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        # calc committee totals
        all_committees = Committee_Overlay.objects.all()
        for sp in all_committees:
            
            all_ies = Expenditure.objects.filter(committee=sp, superceded_by_amendment=False)
            
            dem = all_ies.filter(candidate__party='DEM')   
            total_dem_support = dem.filter(support_oppose='S').aggregate(total=Sum('expenditure_amount'))['total']
            total_dem_oppose = dem.filter(support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total']


            rep = all_ies.filter(candidate__party='REP')
            total_rep_support = rep.filter(support_oppose='S').aggregate(total=Sum('expenditure_amount'))['total']
            total_rep_oppose = rep.filter(support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total']
            
            if total_dem_support:
                sp.ie_support_dems = total_dem_support
            if total_rep_support:
                sp.ie_support_reps = total_rep_support
            if total_dem_oppose:
                sp.ie_oppose_dems = total_dem_oppose
            if total_rep_oppose:
                sp.ie_oppose_reps = total_rep_oppose
            
            total = all_ies.aggregate(total_spent=Sum('expenditure_amount'))
            
            
            if (total['total_spent']):
                print "%s : %s" % (sp.name, total['total_spent'])
                sp.total_indy_expenditures = total['total_spent']
                sp.has_expenditures=True
            else:
                print "%s : %s" % (sp.name, 0)
                sp.total_indy_expenditures = 0
                sp.has_expenditures=False
            
            
            total_pres = Expenditure.objects.filter(committee=sp, superceded_by_amendment=False, office='P').aggregate(total_spent=Sum('expenditure_amount'))
            if (total_pres['total_spent']): 
                sp.total_presidential_indy_expenditures = total_pres['total_spent']
            else:
                sp.total_presidential_indy_expenditures = 0
            
            
            sp.save()
            

        
        
        
                