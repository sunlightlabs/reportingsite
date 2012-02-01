""" Try to attach django models on fields where there are raw ids. This script just does this naively, but more complex matching is possible"""

from django.core.management.base import BaseCommand, CommandError

from rebuckley.models import *

from find_candidate import candidate_lookup

class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the committees table from the committee master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        
        all_iecs = IEOnlyCommittee.objects.filter(fec_id__isnull=False)
        for ie in all_iecs:
            try:
                this_committee = Committee.objects.get(fec_id=ie.fec_id)
                ie.committee_master_record = this_committee
                ie.save()
            except Committee.DoesNotExist:
                #print "Couldn't find committee matching ieonly table: %s %s " % (ie.fec_name, ie.fec_id)
                pass
                
        
        all_ies = Expenditure.objects.filter(committee__isnull=True)       
        for ie in all_ies:
            try:
                this_committee = Committee.objects.get(fec_id=ie.raw_committee_id)
                ie.committee = this_committee
                ie.save()
            except Committee.DoesNotExist:
                #print "Couldn't find committee matching expenditure table: %s %s " % (ie.raw_committee_id, ie.payee)
                pass
                
        all_ies = Expenditure.objects.filter(candidate__isnull=True)
        for ie in all_ies:
            #print "*** Trying to match %s - %s" % (ie.raw_candidate_id, ie.candidate_name)
            try:
                this_candidate = Candidate.objects.get(fec_id=ie.raw_candidate_id, cycle=ie.cycle)
                ie.candidate = this_candidate
                ie.save()
            except Candidate.DoesNotExist:
                
                upper_candidate = str(ie.candidate_name.upper()).strip()
                try:
                    found_id = candidate_lookup[upper_candidate]
                    this_candidate = Candidate.objects.get(fec_id=found_id, cycle=ie.cycle)
                    ie.candidate = this_candidate
                    ie.save()
                    
                except KeyError:
                        
                    pass
                    #print "Couldn't attach candidate to expenditure: %s - %s" % (ie.raw_candidate_id, ie.candidate_name)

        all_contribs = Contribution.objects.all()
        for ac in all_contribs:
            try:
                print "looking for %s" % (ac.fec_committeeid)
                this_superpac = IEOnlyCommittee.objects.get(fec_id=ac.fec_committeeid)
                ac.superpac=this_superpac
                ac.save()
            except IEOnlyCommittee.DoesNotExist:
                print "** Couldn't locate it"
                pass
                
                    