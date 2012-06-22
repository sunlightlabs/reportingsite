import sys

from django.core.management import setup_environ
sys.path.append('/Users/jfenton/reporting/reportingsitenew/reportingsite')

import settings
setup_environ(settings)

from outside_spending.models import Committee_Overlay, Filing_Header
from outside_spending.form_parser import form_parser
from outside_spending.filing import filing

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
        sp.political_orientation = 'U'
        sp.save()
    
print "totals D: %s R: %s" % (total_dem_contribs, total_rep_contribs)
#    total_contribs = sp.total_contributions
    