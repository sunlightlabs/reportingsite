""" Try to attach django models on fields where there are raw ids. 
Need to integrate this with matching thingy. 

"""

from django.core.management.base import BaseCommand, CommandError
from dateutil.parser import parse as dateparse


from outside_spending_2014.models import *

from find_candidate import candidate_lookup
from outside_spending_2014.management.commands.overlay_utils import *
from outside_spending_2014.read_FEC_settings import CYCLE, CYCLE_START, CYCLE_END

cycle_start_date = dateparse(CYCLE_START)
cycle_end_date = dateparse(CYCLE_END)

class Command(BaseCommand):
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        print "starting run"
        all_ies = Expenditure.objects.filter(committee__isnull=True, expenditure_date__gte=cycle_start_date, expenditure_date__lte=cycle_end_date)       
        for ie in all_ies:
            try:
                this_committee = Committee_Overlay.objects.get(fec_id=ie.raw_committee_id)
                ie.committee = this_committee
                ie.committee_name = this_committee.name
                ie.save()
            except Committee_Overlay.DoesNotExist:
                #print "Couldn't find committee matching expenditure table: %s %s " % (ie.raw_committee_id, ie.payee)
                this_committee = get_or_create_committee_overlay(ie.raw_committee_id, CYCLE)
                if (this_committee):
                    ie.committee = this_committee
                    ie.committee_name = this_committee.name
                    ie.save()
                else:
                    print "** missing committee %s " % (ie.raw_committee_id)
                    

        
        print "searching ies"
        missing_candidate_hash = {}
        
        all_ies = Expenditure.objects.filter(candidate__isnull=True, expenditure_date__gte=cycle_start_date, expenditure_date__lte=cycle_end_date)
        for ie in all_ies:
            
            add_to_hash = False
                
            try:
                this_candidate = Candidate_Overlay.objects.get(fec_id=ie.raw_candidate_id, cycle=CYCLE)
                ie.candidate = this_candidate
                ie.save()
                
            except Candidate_Overlay.DoesNotExist:
                
                upper_candidate = str(ie.candidate_name.upper()).strip()
                upper_candidate = upper_candidate.replace('"','')
                
                try:
                    found_id = candidate_lookup[upper_candidate]
                    this_candidate = get_or_create_candidate_overlay(found_id, cycle=CYCLE)
                    if (this_candidate):
                        ie.candidate = this_candidate
                        ie.save()
                    
                except KeyError:
                    this_candidate = get_or_create_candidate_overlay(ie.raw_candidate_id, CYCLE)
                    if (this_candidate):
                        ie.candidate = this_candidate
                        ie.save()
                    else:
                        add_to_hash = True
                        
                    
                else:
                    add_to_hash = True
                    
            if add_to_hash:
                hash_key = "%s|%s|%s" % (ie.candidate_name.upper(), ie.office, ie.state)
                try:
                    missing_candidate_hash[hash_key] = missing_candidate_hash[hash_key] + 1
                except KeyError:
                    missing_candidate_hash[hash_key] = 1
                    
            
        
        # print the missing ids in a hash suitable for running through refine
        # should log this somewhere... 
        print "NAME|OFFICE|STATE|FREQUENCY"
        for a in missing_candidate_hash:
            print a + "|" + str(missing_candidate_hash[a])
                        
                        
        # attach to missing ecs groups. 
        missing_ecs = Electioneering_93.objects.filter(committee__isnull=True)
        for ecs in missing_ecs:
            spending_committee = get_or_create_committee_overlay(ecs.fec_id, CYCLE)
            if (spending_committee):
                ecs.committee =  spending_committee
                ecs.save()
                    
            