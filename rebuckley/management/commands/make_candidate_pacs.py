#  Could probably replace this with a gnarly hunk of sql. This is wildly inefficient, but gets the job done.
#  Not sure how models will change with EC adds. 


## GET OR CREATE IS A FALSE SECURITY BLANKET HERE -- IF A FILING IS AMENDED TO MAKE A CANDIDATE/PAC EXPENDITURE ZERO, THIS PROCEDURE WON'T FIX IT. THUS, PERIODIC DROP/REPLACE IS NECESSARY....


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from rebuckley.models import *

class Command(BaseCommand):
    help = "Sums superpac stuff"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        superpacs = IEOnlyCommittee.objects.all()
        for sp in superpacs:
            
            sp_id = sp.fec_id
            try:
                related_committee = Committee.objects.get(fec_id=sp_id)
            except:
                next 
            # get list of unique candidates supported opposed
            support_list = Expenditure.objects.filter(committee=related_committee, superceded_by_amendment=False, committee__is_superpac=True).values('candidate', 'support_oppose').distinct().order_by()
            for s in support_list:
                total = Expenditure.objects.filter(committee=related_committee, candidate=s['candidate'], support_oppose=s['support_oppose'], superceded_by_amendment=False, committee__is_superpac=True).aggregate(total_spent=Sum('expenditure_amount'))
                related_candidate = Candidate.objects.get(pk=s['candidate'])
                
                print "%s %s %s" % (related_committee, related_candidate, s['support_oppose'])
                
                try: 
                    p = Pac_Candidate.objects.get(committee=related_committee,
                    candidate=related_candidate,
                    support_oppose=s['support_oppose'])
                    
                    p.total_ind_exp = total['total_spent']
                    p.save()
                    
                except Pac_Candidate.DoesNotExist:
                
                    p = Pac_Candidate.objects.create(
                        committee=related_committee,
                        candidate=related_candidate,
                        support_oppose=s['support_oppose'],
                        total_ind_exp = total['total_spent']
                        )
                    p.save()
                    