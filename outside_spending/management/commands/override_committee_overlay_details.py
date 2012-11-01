from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from outside_spending.models import Committee, Committee_Overlay

class Command(BaseCommand):
    args = '<cycle>'
    help = "Set details in the committee overlay from the committee master files. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        # first attach all missing committees
        for co in Committee_Overlay.objects.all():
            if co.committee_master_record:
                pass
            else:
                
                
                try: 
                    correct_co = Committee.objects.get(fec_id = co.fec_id)
                    co.committee_master_record = correct_co
                    co.save()
                    
                except Committee.DoesNotExist:
                    print "missing %s" % (co)
                    
        for co in Committee_Overlay.objects.all():
            if co.committee_master_record:
                co.name = co.committee_master_record.name
                co.treasurer = co.committee_master_record.treasurer                
                co.ctype = co.committee_master_record.ctype  
                co.filing_frequency = co.committee_master_record.filing_frequency  
                co.designation = co.committee_master_record.designation 
                co.connected_org_name = co.committee_master_record.connected_org_name  
                co.interest_group_cat = co.committee_master_record.interest_group_cat 
                                                                                                                
                
            else:
                pass
