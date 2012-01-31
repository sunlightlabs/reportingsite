from django.core.management.base import BaseCommand, CommandError

from rebuckley.models import *

class Command(BaseCommand):
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        for cycle in (2010, 2012):
            print "-- Tests for %s --\n" % (cycle)
            expenditure_count = Expenditure.objects.filter(cycle=cycle).count()
            print "%s Expenditures: %s" % (cycle, expenditure_count)
            
            expenditure_candidates_unidentified = Expenditure.objects.filter(candidate__isnull=True, electioneering_communication=False, cycle=cycle).count()
            print "%s : %sNumber of candidates named as target of independent expenditures that aren't matched to Candidate objects (from the FEC's master file): " % (cycle, expenditure_candidates_unidentified)
            
            office_not_specified = Expenditure.objects.filter(office__isnull=True).count()
            
            print "%s : %s Office not specified: " % (cycle, office_not_specified)
            
            
            for a in ("A1", "A2", "A3", "A4", "A5"):
                amendments = Expenditure.objects.filter(amendment=a, cycle=cycle).count()
                print ("%s : %s Number of %s amendments found -- includes amended amendments") % (cycle, amendments, a)
            
            amendments_ided = Expenditure.objects.filter(superceded_by_amendment=True, cycle=cycle).count()
            print ("%s : %s Number of amended expenditures where the original line was identified ") % (cycle, amendments_ided )
            
            
        print "-- Showing tests aggregate across all years --\n"

        candidate_count = Candidate.objects.count()
        print "Candidates (from master table): %s" % (candidate_count)
        
        
        committee_count = Committee.objects.count()
        print "Committees: (from master table): %s" % (committee_count)
        
        ieoc_count = IEOnlyCommittee.objects.count()
        print "Superpacs: %s" % (ieoc_count)
        
        has_expenditures = IEOnlyCommittee.objects.filter(has_expenditures=True).count()
        print "Number of superpacs with expenditures: %s" % (has_expenditures)
                
        has_pres_expenditures = IEOnlyCommittee.objects.filter(total_presidential_indy_expenditures__gt=0).count()
        print "Superpacs with pres expenditures: %s" % has_pres_expenditures
        
        has_donors = IEOnlyCommittee.objects.filter(has_contributions=True).count()
        print "Has donors: %s" % (has_donors)