""" Utilities for creating committee / candidate overlays from master records"""


from outside_spending_2014.models import Committee, Committee_Overlay, Candidate, Candidate_Overlay
from django.template.defaultfilters import slugify



def get_or_create_committee_overlay(fec_id, cycle):
    """ We can force it to overwrite if we want it updated"""
    
    # make sure it's a string.
    cycle = str(cycle)
    # We're only handling these
    if (cycle not in ('2012', '2014')):
        raise ValueError("Invalid election cycle: %s" % (cycle))
    
    cmte = None
    cmte_overlay = None
    found_committee = True
    found_committee_overlay = True
    
    # Is there already a committee overlay with this name?
    try:
        cmte_ovrly = Committee_Overlay.objects.get(fec_id=fec_id, cycle=cycle)
        return cmte_ovrly
    except Committee_Overlay.DoesNotExist:
        found_committee_overlay = False

    # Get the original record
    try:
        cmte = Committee.objects.get(fec_id=fec_id)
    except Committee.DoesNotExist:
        # if there's no original record, mark it but we can't overwrite later
        found_committee = False

    if (found_committee):
        
        
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
            state = cmte.state_race,
            connected_org_name=cmte.connected_org_name,
            filing_frequency = cmte.filing_frequency,
            committee_master_record = cmte,
            ctype = cmte.ctype,
            designation = cmte.designation,
            
            # 
            is_superpac = cmte.is_superpac,
            is_hybrid = cmte.is_hybrid,
            is_noncommittee = cmte.is_noncommittee,
            
            # this is populated from the FEC, but augmented when we know more
            candidate_id = cmte.candidate_id, 
            candidate_office = cmte.candidate_office)
            
        return cmte_ovrly
        
    return None
    
def overwrite_committee_overlay(fec_id, cycle):
    
    cmte_overlay = None
    
    try:
        cmte_overlay = Committee_Overlay.objects.get(fec_id=fec_id, cycle=cycle)
    except Committee.DoesNotExist:
        get_or_create_committee_overlay(fec_id, cycle)
        return None
    
    # see if we can find a master record, and if we can, overwrite all the data
    
    try: 
        master_committee = Committee.objects.get(fec_id=fec_id)
        
        cmte_overlay.name=master_committee.name
        cmte_overlay.party=master_committee.party
        cmte_overlay.treasurer=master_committee.treasurer
        cmte_overlay.street_1=master_committee.street_1
        cmte_overlay.street_2=master_committee.street_2
        cmte_overlay.city=master_committee.city
        cmte_overlay.zip_code=master_committee.zip_code
        cmte_overlay.state=master_committee.state_race
        cmte_overlay.connected_org_name=master_committee.connected_org_name
        cmte_overlay.filing_frequency=master_committee.filing_frequency
        cmte_overlay.candidate_id=master_committee.candidate_id
        cmte_overlay.candidate_office=master_committee.candidate_office
        cmte_overlay.ctype=master_committee.ctype
        cmte_overlay.designation=master_committee.designation
        
        cmte_overlay.save()

    except Committee.DoesNotExist:
        # we can't do anything
        return None

        
def get_or_create_candidate_overlay(fec_id, cycle, force_overwrite=False):
    # We're only handling these, so far
    cycle = str(cycle)
    if (cycle not in ('2012', '2014')):
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
      

    get_or_create_candidate_overlay('H0AK00089', 2014)
    get_or_create_candidate_overlay('H0AL05155', 2014)