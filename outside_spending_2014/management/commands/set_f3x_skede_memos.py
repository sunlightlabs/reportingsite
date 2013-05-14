""" hack to correctly set the memo code on F3X sked E's; this wasn't being set right initially"""

from django.core.management.base import BaseCommand
from dateutil.parser import parse as dateparse

from outside_spending_2014.models import Expenditure, F3X_Summary

from outside_spending_2014.form_parser import form_parser
from outside_spending_2014.filing import filing

def handle_filing_num(filingnum, fp):
    f1 = filing(filingnum, True, True)
    f1.download()

    formtype = f1.get_form_type()
    version = f1.version
    
    firstrow = fp.parse_form_line(f1.get_first_row(), version)    
    #print firstrow
    committee_id = firstrow['filer_committee_id_number']
    committee_name = firstrow['committee_name']

    #print "id: %s committee: %s" % (committee_id, committee_name)

    schedule_e_lines = f1.get_rows('SE')
    if len(schedule_e_lines)==0:
        # There's nothing here for us, so quit.
        return 0

    headers = f1.get_headers()
    is_amendment = headers['is_amendment']

    original=None
    if (is_amendment):
        original=headers['filing_amended']    

    for e_line in schedule_e_lines:
        thisrow = fp.parse_form_line(e_line, version)        
        #print "\nGot sked E line: %s\n" % (thisrow)
        transaction_id = thisrow['transaction_id_number']

        memo_text_description=''
        try:
            memo_text_description=thisrow['memo_text_description']
        except KeyError:
            pass

        
        memo_code = ''
        try:
            memo_code =thisrow['memo_code']
        except KeyError:
            pass
        
        if memo_code: 
            
            
            # Now we gotta find the line as it exists in the db and modify the memo code and memo_text_description. Don't create it if it doesn't exist.
            try:
                this_transaction = Expenditure.objects.get(filing_number=filingnum, transaction_id=transaction_id)
                print "Got memoed F3X line! %s %s %s - amount= %s" % (filingnum, transaction_id, memo_code, thisrow['expenditure_amount'])
                this_transaction.memo_code = memo_code
                this_transaction.memo_text_description = memo_text_description
                
                this_transaction.save()
                
            except Expenditure.DoesNotExist:
                print "Missing memoed transaction %s %s %s" % (filingnum, transaction_id, memo_code)


class Command(BaseCommand):
    def handle(self, *args, **options):
        fp = form_parser()
        
        all_f3xwsked_es = F3X_Summary.objects.filter(total_sched_e__gte=0).values('filing_number')
        for filing in all_f3xwsked_es:
            this_filing_number = filing['filing_number']
            handle_filing_num(this_filing_number, fp)
        