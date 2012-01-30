from django.core.management.base import BaseCommand, CommandError
# By attaching expenditures to candidates--even when the candidate id is missing--we've created 
# a new way to look for office information for expenditures where it's missing: assign the expenditure
# the office of the candidate it's supporting / opposing. 


from rebuckley.models import *

class Command(BaseCommand):
    requires_model_validation = False
    
    def handle(self, *args, **options):
        for cycle in (2010, 2012):
                expenditures = Expenditure.objects.filter(cycle=cycle)
                for e in expenditures:
                    if (e.candidate):
                        print "candidate's office = %s ; expenditure office: %s" % (e.candidate.office, e.office)
                        if ( ( e.office == '' or e.office==' ')  and e.office.upper() != e.candidate.office.upper()):
                            if ( e.office == '' or e.office==' '): 
                                e.office = e.candidate.office.upper().strip()
                                e.save()
                                
                                
                            print "Mismatch '%s' - '%s' " % (e.office, e.candidate.office)
                    else:
                        print "Missing candidate: %s " % (e.candidate_name) 
                        