import sys

from django.core.management import setup_environ
#sys.path.append('/Users/jfenton/reporting/reportingsitenew/reportingsite')
sys.path.append('/projects/reporting/src/reportingsite')

import settings
setup_environ(settings)

from outside_spending.models import Committee_Overlay, Filing_Header, Expenditure
from outside_spending.form_parser import form_parser
from outside_spending.filing import filing
from django.db.models import Sum

from dateutil.parser import parse as dateparse



superpacs = Committee_Overlay.objects.filter(is_superpac=True, total_indy_expenditures__gt=0).order_by('-total_contributions')
total_dem_contribs = 0
total_rep_contribs = 0
for sp in superpacs:
    ie_support_dems = sp.ie_support_dems
    ie_oppose_dems = sp.ie_oppose_dems
    ie_support_reps = sp.ie_support_reps
    ie_oppose_reps = sp.ie_oppose_reps
    total_contributions = 0
    if (sp.total_contributions):
        total_contributions = sp.total_contributions
    #print "-- %s total contribs is %s" % (sp.name, total_contributions)
    if (ie_support_dems > 0 and ie_support_reps == 0):
        
        if sp.political_orientation != 'D':
            print "ERROR!! %s supports dems ; pro_dem: %s anti_dem: %s pro_rep: %s anti_rep: %s" % (sp.name, ie_support_dems, ie_oppose_dems, ie_support_reps, ie_oppose_reps)

    elif (ie_support_reps > 0 and ie_support_dems == 0):
        if sp.political_orientation != 'R':
            
            print "ERROR!! %s supports reps ; pro_dem: %s anti_dem: %s pro_rep: %s anti_rep: %s" % (sp.name, ie_support_dems, ie_oppose_dems, ie_support_reps, ie_oppose_reps)

    elif (ie_support_reps > 0 and ie_support_dems > 0):
        print "*** %s is_ambiguous reps ; pro_dem: %s anti_dem: %s pro_rep: %s anti_rep: %s" % (sp.name, ie_support_dems, ie_oppose_dems, ie_support_reps, ie_oppose_reps)
       
        
        
    ## now look at primary spending and general election spending
    elif (ie_support_reps == 0 and ie_support_dems == 0 and (ie_oppose_reps > 0 or ie_oppose_dems > 0 ) ):
        
        # flags
        only_played_in_rep_primary = False
        only_played_in_dem_primary = False        
        opposed_dems_in_general = False
        opposed_reps_in_general = False
        
        
        #print "***Pure negative: %s" % sp.name
        ies = Expenditure.objects.filter(committee=sp, superceded_by_amendment=False)
        
        election_data = ""
        for election_type in ('P', 'G'):
            
            all_ies = ies.filter(election_type=election_type)
        
            dem = all_ies.filter(candidate__party='DEM')   
            total_dem_oppose = dem.filter(support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total']

            rep = all_ies.filter(candidate__party='REP')
            total_rep_oppose = rep.filter(support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total']

            if not total_dem_oppose: 
                total_dem_oppose = 0
            if not total_rep_oppose:
                total_rep_oppose = 0

            # set flags
            if (election_type == 'P'):
                if (total_dem_oppose > 0 and total_rep_oppose == 0):
                    only_played_in_dem_primary = True
                elif (total_dem_oppose == 0 and total_rep_oppose > 0):
                    only_played_in_rep_primary = True
            if (election_type == 'G'):
                if (total_dem_oppose > 0):
                    opposed_dems_in_general = True
                if (total_rep_oppose > 0):
                    opposed_reps_in_general = True
            
            election_data +=  "%s - For election type %s dem oppose: %s rep oppose: %s\n" % (sp.name, election_type, total_dem_oppose, total_rep_oppose)
            
        if (only_played_in_rep_primary and not opposed_reps_in_general):
            if sp.political_orientation != 'R':
                print "WARNING: %s Presumed Republican - only played in republican primary and didn't play in general" % (sp.name)
                print election_data

            
        if (only_played_in_dem_primary and not opposed_dems_in_general):
            if sp.political_orientation != 'D':
                print "WARNING: %s Presumed Democrat - only played in democratic primary and didn't play in general " % (sp.name)
                print election_data
        if (opposed_dems_in_general and not only_played_in_rep_primary):
            if sp.political_orientation != 'R':
                print "WARNING: %s Presumed Republican - didn't only play in republican primary but opposed dems in general" % (sp.name)
                print election_data

        if (opposed_reps_in_general and not only_played_in_dem_primary):
            if sp.political_orientation != 'R':
                print "WARNING: %s Presumed Republican - didn't only play in democatic primary but opposed reps in general" % (sp.name)  
                print election_data 
        
        
        if ( (only_played_in_dem_primary and opposed_dems_in_general) or (only_played_in_rep_primary and opposed_reps_in_general )):
            print "!!!! confusing:%s" % (sp.name)
            print election_data
            sp.political_orientation = 'U'
            # but don't save it! 

    