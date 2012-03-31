""" Try to attach django models on fields where there are raw ids. This script just does this naively, but more complex matching is possible"""

from django.core.management.base import BaseCommand, CommandError

from outside_spending.models import *

from find_candidate import candidate_lookup
from outside_spending.management.commands.overlay_utils import *
cycle = 2012

class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the committees table from the committee master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        all_ies = Expenditure.objects.filter(committee__isnull=True)       
        for ie in all_ies:
            try:
                this_committee = Committee_Overlay.objects.get(fec_id=ie.raw_committee_id)
                ie.committee = this_committee
                ie.committee_name = this_committee.name
                ie.save()
            except Committee_Overlay.DoesNotExist:
                #print "Couldn't find committee matching expenditure table: %s %s " % (ie.raw_committee_id, ie.payee)
                this_committee = get_or_create_committee_overlay(ie.raw_committee_id, cycle)
                if (this_committee):
                    ie.committee = this_committee
                    ie.committee_name = this_committee.name
                    ie.save()
                else:
                    print "** missing committee %s " % (ie.raw_committee_id)
                    

                
        all_ies = Expenditure.objects.filter(candidate__isnull=True)
        for ie in all_ies:
            #print "*** Trying to match %s - %s" % (ie.raw_candidate_id, ie.candidate_name)
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
                    
                        
                        

                    #print "Couldn't attach candidate to expenditure: %s - %s" % (ie.raw_candidate_id, ie.candidate_name)

        all_contribs = Contribution.objects.all()
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
