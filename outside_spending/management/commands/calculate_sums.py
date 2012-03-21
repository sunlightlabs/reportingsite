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
        
            total = Expenditure.objects.filter(committee=sp, superceded_by_amendment=False).aggregate(total_spent=Sum('expenditure_amount'))
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
            

        
        
        
                