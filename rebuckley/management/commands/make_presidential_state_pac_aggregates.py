#  Could probably replace this with a gnarly hunk of sql. This is wildly inefficient, but gets the job done.
#  Not sure how models will change with EC adds. 


## GET OR CREATE IS A FALSE SECURITY BLANKET HERE -- IF A FILING IS AMENDED TO MAKE A CANDIDATE/PAC EXPENDITURE ZERO, THIS PROCEDURE WON'T FIX IT. THUS, PERIODIC DROP/REPLACE IS NECESSARY....
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from rebuckley.models import *

today = datetime.date.today()
two_weeks_ago = today - datetime.timedelta(days=14)

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
            # get list of unique presidential candidates supported and opposed by state
            support_list = Expenditure.objects.filter(committee=related_committee, superceded_by_amendment=False, committee__is_superpac=True, office='P').values('candidate', 'support_oppose', 'state').distinct().order_by()
            for s in support_list:
                total = Expenditure.objects.filter(committee=related_committee, candidate=s['candidate'], support_oppose=s['support_oppose'], state=s['state'], superceded_by_amendment=False, committee__is_superpac=True).aggregate(total_spent=Sum('expenditure_amount'))
                related_candidate = Candidate.objects.get(pk=s['candidate'])
                total_recent = Expenditure.objects.filter(committee=related_committee, candidate=s['candidate'], support_oppose=s['support_oppose'], state=s['state'], superceded_by_amendment=False, committee__is_superpac=True, expenditure_date__gte=two_weeks_ago).aggregate(total_spent=Sum('expenditure_amount'))
                related_candidate = Candidate.objects.get(pk=s['candidate'])
                
                print "%s %s %s %s" % (related_committee, related_candidate, s['support_oppose'], s['state'])
                
                try: 
                    p = President_State_Pac_Aggregate.objects.get(committee=related_committee,
                    candidate=related_candidate,
                    support_oppose=s['support_oppose'], 
                    state=s['state'])
                    
                    p.expenditures = total['total_spent']
                    p.recent_expenditures=total_recent['total_spent']
                    p.save()
                    
                except President_State_Pac_Aggregate.DoesNotExist:
                
                    p = President_State_Pac_Aggregate.objects.create(
                        committee=related_committee,
                        candidate=related_candidate,
                        support_oppose=s['support_oppose'],
                        state=s['state'],
                        expenditures = total['total_spent'],
                        recent_expenditures=total_recent['total_spent']
                        )
                    p.save()
                    