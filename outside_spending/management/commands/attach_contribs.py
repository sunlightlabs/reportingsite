from outside_spending.models import *

from django.core.management.base import BaseCommand, CommandError
from find_candidate import candidate_lookup
from outside_spending.management.commands.overlay_utils import *
cycle = 2012

class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the committees table from the committee master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        
        all_contribs = Contribution.objects.filter(committee__isnull=True)
        for ac in all_contribs:
            try:
                #print "looking for %s" % (ac.fec_committeeid)
                this_committee = Committee_Overlay.objects.get(fec_id=ac.fec_committeeid)
                ac.committee=this_committee
                ac.save()
            except Committee_Overlay.DoesNotExist:
                print "** Couldn't locate it"
                pass
            #