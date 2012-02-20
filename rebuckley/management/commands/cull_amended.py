from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from rebuckley.models import Expenditure

class Command(BaseCommand):
    help = "Remove amended filings"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        # fix the amendments one at a time
        for a in (1, 2, 3,  4, 5):
            a_type = "A" + str(a)
            list_of_earlier_amendments = ['N']
            for i in range(1,a):
                list_of_earlier_amendments.append('A' + str(i))
            print "Handling %s with earlier_amendments %s" % (a_type, list_of_earlier_amendments)
            
            all_current_amendments = Expenditure.objects.filter(amendment=a_type, amends_earlier_filing=False)
            print "Length is: %s" % (len(all_current_amendments))
            
            for this_amendment in all_current_amendments:
                print 
                presumed_dupe = Expenditure.objects.filter(transaction_id=this_amendment.transaction_id, raw_committee_id=this_amendment.raw_committee_id, amendment__in=list_of_earlier_amendments, superceded_by_amendment=False, cycle=this_amendment.cycle)
                for dupe in presumed_dupe:
                    print "Found dupe to: %s %s $%s" % (this_amendment.raw_committee_id, this_amendment.id, this_amendment.expenditure_amount)
                    dupe.amended_by=this_amendment.id
                    dupe.superceded_by_amendment=True
                    dupe.save()
                    
                    this_amendment.amends_earlier_filing = True
                    this_amendment.save()
                    
                else:
                    print "Couldn't find dupe to: %s %s $%s " % (this_amendment.raw_committee_id, this_amendment.id, this_amendment.expenditure_amount)