from outside_spending.models import *
from outside_spending.management.commands.find_candidate import candidate_lookup


def attach_candidate(ie):
    try:
        this_candidate = Candidate_Overlay.objects.get(fec_id=ie.raw_candidate_id, cycle=int(ie.cycle))
        ie.candidate = this_candidate
        ie.save()
    except Candidate_Overlay.DoesNotExist:
        
        upper_candidate = str(ie.candidate_name.upper()).strip()
        
        try:
            found_id = candidate_lookup[upper_candidate]
            this_candidate = get_or_create_candidate_overlay(found_id, cycle=int(ie.cycle))
            if (this_candidate):
                ie.candidate = this_candidate
                ie.save()
            
        except KeyError:
            this_candidate = get_or_create_candidate_overlay(ie.raw_candidate_id, cycle)
            if (this_candidate):
                ie.candidate = this_candidate
                ie.save()
                
