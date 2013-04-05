from django.core.management.base import BaseCommand, CommandError
# By attaching expenditures to candidates--even when the candidate id is missing--we've created 
# a new way to look for office information for expenditures where it's missing: assign the expenditure
# the office of the candidate it's supporting / opposing. 


from outside_spending.models import *

class Command(BaseCommand):
    requires_model_validation = False
    
    def handle(self, *args, **options):
        for cycle in (2010, 2012):
                expenditures = Expenditure.objects.filter(cycle=cycle)
                for e in expenditures:
                    if (e.candidate):
                        #print "candidate's office = %s ; expenditure office: %s" % (e.candidate.office, e.office)
                        if ( ( e.office == '' or e.office==' ') ):
                            if ( (e.candidate.office.upper()=='P' or e.candidate.office.upper()=='H' or e.candidate.office.upper()=='S' ) ): 
                                e.office = e.candidate.office.upper().strip()
                                e.save()
                                print "Fixing '%s' to '%s' " % (e.office, e.candidate.office)
                                
                       
                        if ( e.state == '' or e.state==' '):
                            candidate_id = e.candidate.fec_id
                            candidate_state_abbrev = candidate_id[2:4]
                            candidate_office = candidate_id[0]
                            if (candidate_office == 'P'):
                                #print "Presidential district: %s" % e.candidate.district
                                pass
                            #print "Got state %s abbrev: %s" % (candidate_id, candidate_state_abbrev)
                        
                    else:
                        print "Missing candidate: %s " % (e.candidate_name) 
                        