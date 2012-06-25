import sys

from django.core.management import setup_environ
sys.path.append('/Users/jfenton/reporting/reportingsitenew/reportingsite')

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
    #print "total contribs is %s" % (total_contributions)
    if (ie_support_dems > 0 and ie_support_reps == 0):
        print "%s supports dems ; pro_dem: %s anti_dem: %s pro_rep: %s anti_rep: %s" % (sp.name, ie_support_dems, ie_oppose_dems, ie_support_reps, ie_oppose_reps)
        sp.political_orientation = 'D'
        sp.save()
        total_dem_contribs += total_contributions
    elif (ie_support_reps > 0 and ie_support_dems == 0):
        print "%s supports reps ; pro_dem: %s anti_dem: %s pro_rep: %s anti_rep: %s" % (sp.name, ie_support_dems, ie_oppose_dems, ie_support_reps, ie_oppose_reps)
        total_rep_contribs += total_contributions
        sp.political_orientation = 'R'
        sp.save()
    elif (ie_support_reps > 0 and ie_support_dems > 0):
        print "*** %s is_ambiguous reps ; pro_dem: %s anti_dem: %s pro_rep: %s anti_rep: %s" % (sp.name, ie_support_dems, ie_oppose_dems, ie_support_reps, ie_oppose_reps)
        # Don't save, because we've probably set it by hand.
        #sp.political_orientation = 'U'
        #sp.save()
        
        
    ## now look at primary spending and general election spending
    elif (ie_support_reps == 0 and ie_support_dems == 0 and (ie_oppose_reps > 0 or ie_oppose_dems > 0 ) ):
        
        # flags
        only_played_in_rep_primary = False
        only_played_in_dem_primary = False        
        opposed_dems_in_general = False
        opposed_reps_in_general = False
        
        
        #print "***Pure negative: %s" % sp.name
        ies = Expenditure.objects.filter(committee=sp, superceded_by_amendment=False)
        
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
            
            print "\t%s - For election type %s dem oppose: %s rep oppose: %s" % (sp.name, election_type, total_dem_oppose, total_rep_oppose)
            
        if (only_played_in_rep_primary and not opposed_reps_in_general):
            print "%s Presumed Republican - only played in republican primary and didn't play in general" % (sp.name)
            sp.political_orientation = 'R'
            sp.save()
            
        if (only_played_in_dem_primary and not opposed_dems_in_general):
            print "%s Presumed Democrat - only played in democratic primary and didn't play in general " % (sp.name)
            sp.political_orientation = 'D'
            sp.save()
        if ( (only_played_in_dem_primary and opposed_dems_in_general) or (only_played_in_rep_primary and opposed_reps_in_general )):
            print "!!!! confusing:%s" % (sp.name)
            
        
print "totals D: %s R: %s" % (total_dem_contribs, total_rep_contribs)
#    total_contribs = sp.total_contributions
    