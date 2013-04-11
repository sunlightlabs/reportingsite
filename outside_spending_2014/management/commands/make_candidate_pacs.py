#  Could probably replace this with a gnarly hunk of sql. This is wildly inefficient, but gets the job done.
#  Not sure how models will change with EC adds. 


## GET OR CREATE IS A FALSE SECURITY BLANKET HERE -- IF A FILING IS AMENDED TO MAKE A CANDIDATE/PAC EXPENDITURE ZERO, THIS PROCEDURE WON'T FIX IT. THUS, PERIODIC DROP/REPLACE IS NECESSARY....


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending_2014.models import *
from outside_spending_2014.read_FEC_settings import CYCLE, CYCLE_START, CYCLE_END

class Command(BaseCommand):
    help = "Sums superpac stuff"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        committees = Committee_Overlay.objects.filter(cycle=CYCLE)
        for sp in committees:
            
            support_list = Expenditure.objects.filter(committee=sp, cycle=CYCLE, superceded_by_amendment=False).values('candidate', 'support_oppose').distinct().order_by()
            for s in support_list:
                total = Expenditure.objects.filter(committee=sp, candidate=s['candidate'], support_oppose=s['support_oppose'], superceded_by_amendment=False, cycle=CYCLE).aggregate(total_spent=Sum('expenditure_amount'))
                
                if not s['candidate']:
                    continue
                
                related_candidate = Candidate_Overlay.objects.get(pk=s['candidate'], cycle=CYCLE)
                
                print "%s %s %s" % (sp, related_candidate, s['support_oppose'])
                
                try: 
                    p = Pac_Candidate.objects.get(committee=sp, candidate=related_candidate, support_oppose=s['support_oppose'], cycle=CYCLE)
                    p.total_ind_exp = total['total_spent']
                    p.save()
                    
                except Pac_Candidate.DoesNotExist:
                
                    p = Pac_Candidate.objects.create(
                        cycle=CYCLE,
                        committee=sp,
                        candidate=related_candidate,
                        support_oppose=s['support_oppose'],
                        total_ind_exp = total['total_spent']
                        )
                    p.save()
                    
