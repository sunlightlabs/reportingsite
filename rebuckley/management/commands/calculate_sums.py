from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from rebuckley.models import *

class Command(BaseCommand):
    help = "Sums superpac stuff"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        # calc superpac totals
        all_superpacs = IEOnlyCommittee.objects.all()
        for sp in all_superpacs:
        
            total = Expenditure.objects.filter(raw_committee_id=sp.fec_id, superceded_by_amendment=False).aggregate(total_spent=Sum('expenditure_amount'))
            if (total['total_spent']):
                print "%s : %s" % (sp.fec_name, total['total_spent'])
                sp.total_indy_expenditures = total['total_spent']
                sp.has_expenditures=True
            else:
                print "%s : %s" % (sp.fec_name, 0)
                sp.total_indy_expenditures = 0
                sp.has_expenditures=False
            
            
            total_pres = Expenditure.objects.filter(raw_committee_id=sp.fec_id, superceded_by_amendment=False, office='P').aggregate(total_spent=Sum('expenditure_amount'))
            if (total_pres['total_spent']): 
                sp.total_presidential_indy_expenditures = total_pres['total_spent']
            else:
                sp.total_presidential_indy_expenditures = 0
            
            
            sp.save()
            
        # calc committee totals:
        all_committees = Committee.objects.all()
        for cm in all_committees:
            expenditures = Expenditure.objects.filter(superceded_by_amendment=False,committee=cm).aggregate(total_spent=Sum('expenditure_amount'))
            if (expenditures['total_spent']):
                cm.total_expenditures = expenditures['total_spent']
                cm.has_expenditures = True
            else:
                cm.total_expenditures = 0
                cm.has_expenditures = False
            
            cm.save()
                
        # Make the pac-candidate rows -- should we kill all these lines out first ? Hmm. Probably we should in the unlikely event that an expenditure is list as going to the wrong person, and then amended, but... 
        
        
        
        
                