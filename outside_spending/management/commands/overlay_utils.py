""" Utilities for creating committee / candidate overlays from master records"""

from outside_spending.models import Committee, Committee_Overlay, Candidate, Candidate_Overlay
from django.template.defaultfilters import slugify

def get_or_create_committee_overlay(fec_id, cycle, force_overwrite=False):
    """ We can force it to overwrite if we want it updated"""
    
    # We're only handling these, so far
    if (cycle not in (2010, 2012)):
        raise ValueError("Invalid election cycle: %s" % (cycle))
    
    cmte = None
    
    # Get the original record
    try:
        cmte = Committee.objects.get(fec_id=fec_id)
    except Committee.DoesNotExist:
        # if there's no original record, so there's nothing to be done
        return None
    
    try:
        cmte_ovrly = Committee_Overlay.objects.get(fec_id=fec_id, cycle=cycle)
        
        if (force_overwrite):
            cmte_ovrly.cycle = cycle,
            cmte_ovrly.name = cmte.name,
            cmte_ovrly.slug = cmte.slug,
            cmte_ovrly.party = cmte.party,
            cmte_ovrly.treasurer = cmte.treasurer,
            cmte_ovrly.street_1 = cmte.street_1,
            cmte_ovrly.street_2 = cmte.street_2,
            cmte_ovrly.city =cmte.city,
            cmte_ovrly.zip_code = cmte.zip_code,
            cmte_ovrly.state_race = cmte.state_race,
            cmte_ovrly.connected_org_name=cmte.connected_org_name,
            cmte_ovrly.filing_frequency = cmte.filing_frequency,
            cmte_ovrly.candidate_id = cmte.candidate_id, 
            cmte_ovrly.candidate_office = cmte.candidate_office,
            cmte_ovrly.committee_master_record = cmte
            
            cmte_ovrly.save()
        return cmte_ovrly
        
    except Committee_Overlay.DoesNotExist:
        # We can't find the overlay, so copy the fields from the raw record
        
        cmte_ovrly = Committee_Overlay.objects.create(
            cycle=cycle,
            name = cmte.name,
            fec_id = fec_id,
            slug = cmte.slug,
            party = cmte.party,
            treasurer = cmte.treasurer,
            street_1 = cmte.street_1,
            street_2 = cmte.street_2,
            city =cmte.city,
            zip_code = cmte.zip_code,
            state_race = cmte.state_race,
            connected_org_name=cmte.connected_org_name,
            filing_frequency = cmte.filing_frequency,
            committee_master_record = cmte,
            
            # this is populated from the FEC, but augmented when we know more
            candidate_id = cmte.candidate_id, 
            candidate_office = cmte.candidate_office)
            
        return cmte_ovrly
        
def get_or_create_candidate_overlay(fec_id, cycle, force_overwrite=False):
    # We're only handling these, so far
    if (cycle not in (2010, 2012)):
        raise ValueError("Invalid election cycle: %s" % (cycle))
    
    cand = None
    
    # Get the original record
    try:
        cand = Candidate.objects.get(fec_id=fec_id, cycle=cycle)
    except Candidate.DoesNotExist:
        # if there's no original record, there's nothing to be done
        return None
        
    
    try:
        cand_ovrly = Candidate_Overlay.objects.get(fec_id=fec_id, cycle=cycle)
        
        cand_slug = slugify(cand.fec_name)
        
        if (force_overwrite):
                cand_ovrly.slug = cand_slug,
                cand_ovrly.fec_name=cand.fec_name,
                cand_ovrly.party=cand.party,
                cand_ovrly.office=cand.office, 
                cand_ovrly.seat_status=cand.seat_status, 
                cand_ovrly.candidate_status=cand.candidate_status,                                
                cand_ovrly.state_address=cand.state_address,
                cand_ovrly.district=cand.district,
                cand_ovrly.state_race=cand.state_race,
                cand_ovrly.campaign_com_fec_id=cand.campaign_com_fec_id
                        
                cand_ovrly.save()
            
        return cand_ovrly       
                
        
    except Candidate_Overlay.DoesNotExist:
        
        
        cand_slug = slugify(cand.fec_name)
        
        cand_ovrly = Candidate_Overlay.objects.create(
            cycle=cycle,
            slug=cand_slug,
            fec_id=fec_id,
            fec_name=cand.fec_name,
            party=cand.party,
            office=cand.office, 
            seat_status=cand.seat_status, 
            candidate_status=cand.candidate_status,                                
            state_address=cand.state_address,
            district=cand.district,
            state_race=cand.state_race,
            campaign_com_fec_id=cand.campaign_com_fec_id
        )
        
        return cand_ovrly
    
def test_run():
#    get_or_create_committee_overlay('C90012659', 2012)
#    get_or_create_committee_overlay('C90012758', 2012)
#    get_or_create_committee_overlay('C90012782', 2012)            
#    get_or_create_committee_overlay('C90012832', 2011)
#    get_or_create_committee_overlay('C90012576', 2012)        

    get_or_create_candidate_overlay('H0AK00089', 2012)
    get_or_create_candidate_overlay('H0AL05155', 2012)