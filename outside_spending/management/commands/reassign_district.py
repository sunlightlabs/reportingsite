""" To deal with redistricting. """

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
import re

from outside_spending.models import *

class Command(BaseCommand):
    help = "Resets district in candidate_overlay, erases pac_candidate aggregate entry"
    requires_model_validation = False


    def handle(self, *args, **options):
        
        candidate_id = args[0]
        new_district = args[1]
        
        assert candidate_id, "You must enter a committee id"
        assert new_district, "You must enter a new district number"
        
        committee_regex = re.compile('\AH\d\w{2}\d{5}\Z')
        assert committee_regex.match(candidate_id), "Invalid candidate id: '%s'" % (candidate_id)
        
        district_regex = re.compile('\A\d\d\Z')
        assert district_regex.match(new_district), "Invalid district: '%s'. Be sure to include leading zeroes for single-digit districts, i.e. '03' " % (new_district)
        
        candidate_to_reassign = Candidate_Overlay.objects.get(fec_id=candidate_id)
        old_district = candidate_to_reassign.district
        state = candidate_to_reassign.state_race
        assert old_district != new_district, "Old district is the same as new district. No change."
        
        
        print "Reassigning candidate %s from district %s to district %s in %s" % (candidate_to_reassign, old_district, new_district, state)
        candidate_to_reassign.district = new_district
        candidate_to_reassign.save()
        
        # Now delete the race aggregate
        try:
            old_aggregate = Race_Aggregate.objects.get(state=state, district=old_district)
            old_aggregate.delete()
            print "Deleted race aggregate total; recreate with manage.py make_race_aggregates"
        except Race_Aggregate.DoesNotExist:
            print "Couldn't find old race aggregate"
            pass
        
            
        
        