


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from rebuckley.models import *

class Command(BaseCommand):
    help = "Create race aggregates"
    requires_model_validation = False


    def handle(self, *args, **options):
        candidate_ids = Expenditure.objects.filter(superceded_by_amendment=False, committee__is_superpac=True).values('candidate__fec_id').distinct().order_by()
        
        for candidate_id in candidate_ids:
            # ignore nulls
            if (candidate_id['candidate__fec_id']):
                print "Looking for %s" % candidate_id
                candidate = Candidate.objects.get(fec_id=candidate_id['candidate__fec_id'])
                total_supporting = Expenditure.objects.filter(superceded_by_amendment=False, candidate=candidate, support_oppose__iexact='S', committee__is_superpac=True).aggregate(total=Sum('expenditure_amount'))
                total_opposing = Expenditure.objects.filter(superceded_by_amendment=False, candidate=candidate, support_oppose__iexact='O', committee__is_superpac=True).aggregate(total=Sum('expenditure_amount'))
                total = Expenditure.objects.filter(superceded_by_amendment=False, candidate=candidate, committee__is_superpac=True).aggregate(total=Sum('expenditure_amount'))
            
                print "%s : %s %s %s" % (candidate.fec_name, total_supporting['total'], total_opposing['total'], total['total'])
                
                
                    
                candidate.expenditures_supporting = total_supporting['total']
                candidate.expenditures_opposing = total_opposing['total']
                candidate.total_expenditures = total['total']
                candidate.save()

              