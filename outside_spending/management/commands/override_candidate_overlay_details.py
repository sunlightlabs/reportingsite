from django.core.management.base import BaseCommand, CommandError

from outside_spending.models import Candidate, Candidate_Overlay

class Command(BaseCommand):
    args = '<cycle>'
    help = "Set details in the candidate overlay from the candidate master files. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
                    
        for co in Candidate_Overlay.objects.all():
            try:
                candidate_master_record = Candidate.objects.get(fec_id=co.fec_id)
                co.fec_name = candidate_master_record.fec_name
                co.party = candidate_master_record.party           
                co.office = candidate_master_record.office
                co.seat_status = candidate_master_record.seat_status
                co.candidate_status = candidate_master_record.candidate_status
                co.state_race = candidate_master_record.state_race
                co.district = candidate_master_record.district
                co.campaign_com_fec_id = candidate_master_record.campaign_com_fec_id
                co.save()                                                                             
                
            except Candidate.DoesNotExist:
                print "Missing candidate %s" % (co)
                pass
