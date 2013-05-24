from outside_spending.filing import filing

from form_helpers import process_F24
import re

# process a monthly f5. Typically we exclude these because they aren't consistently filed and some are empty, I think, so overriding F24's would be erasing data, potentially. This is the messiest piece of IE handly, probably.

""" Handle basic ie process files -- F3X, F5, F24"""    
def process_monthly_F5_expenditures(filingnum, fp):
    f1 = filing(filingnum, True, True)
    f1.download()
    form = f1.get_form_type()
    version = f1.get_version()
    headers = f1.get_headers()
    is_amendment = headers['is_amendment']
    original=None
    filer_id = headers['fec_id']
    if (is_amendment):
        original=headers['filing_amended']
    
    

        
    if (re.match('^F5', form)):
        parsed_line = fp.parse_form_line(f1.get_first_row(), version)
        print "\n***%s:  %s - %s\n %s - %s" % (filingnum, parsed_line['report_code'], parsed_line['report_type'],  parsed_line['coverage_from_date'],  parsed_line['coverage_through_date'])
        if (parsed_line['report_type']!='24' and parsed_line['report_type']!='48'):
            process_F24(filingnum, fp)
            
        else:
            print "this is a 24- or 48-hr form. Skipping!"
