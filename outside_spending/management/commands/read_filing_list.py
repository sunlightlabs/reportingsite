from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from outside_spending.models import *

from outside_spending.form_parser import form_parser
from outside_spending.filing import filing

import csv

fp = form_parser()
dumpfilename = "outside_spending/data/F3X_sbdump.csv"

def map_parsed_line(line):
    ordered_list = (line['form_type'], line['transaction_id_number'], line['expenditure_date'], line['expenditure_amount'], line['entity_type'],  line['payee_first_name'], line['payee_last_name'], line['payee_organization_name'], line['payee_street_1'], line['payee_street_2'], line['payee_city'], line['filer_committee_id_number'], line['expenditure_purpose_descrip'], line['beneficiary_committee_name'], line['beneficiary_committee_fec_id'], line['conduit_name'], line['conduit_city'], line['conduit_state'], line['memo_code'])
    print ordered_list
    
def process_file(filingnum, csvwriter):
    f1 = filing(filingnum)
    f1.download()
    form = f1.get_form_type()
    version = f1.get_version()

    # only parse forms that we're set up to read
    
    if not fp.is_allowed_form(form):
        print "Not a parseable form: %s - %s" % (form, filingnum)
        return


    print "Found form: %s - %s" % (form, filingnum)
    #rows =  f1.get_all_rows()
    rows = f1.get_rows('^SB')
    #print "rows: %s" % rows
    for row in rows:
        # the last line is empty, so don't try to parse it
        if len(row)>1:
            print "in filing: %s" % filingnum
            parsed_line = fp.parse_form_line(row, version)
            #map_parsed_line(parsed_line)
            csvwriter.writerow(parsed_line)





class Command(BaseCommand):
    help = "Reads a file, dumps it"
    requires_model_validation = False


    def handle(self, *args, **options):
        field_list = ['expenditure_amount', 'expenditure_date','form_type', 'transaction_id_number', 'expenditure_date', 'expenditure_amount', 'entity_type',  'payee_first_name', 'payee_last_name', 'payee_organization_name', 'payee_street_1', 'payee_street_2', 'payee_city', 'filer_committee_id_number', 'expenditure_purpose_descrip', 'beneficiary_committee_name', 'beneficiary_committee_fec_id', 'conduit_name', 'conduit_city', 'conduit_state', 'memo_code']
        outfile = open(dumpfilename, 'w')
        header = ''
        for i in field_list:
            header = header + i + ", "
        outfile.write(header + "\n")
        csvwriter = csv.DictWriter(outfile, field_list, restval='', extrasaction='ignore')
        
        
        
        # calc committee totals
        superpacs = Committee_Overlay.objects.filter(is_superpac=True)
        
        for sp in superpacs:
            #sp = Committee_Overlay.objects.get(fec_id=)

            print "Handling superpac: %s - %s" % (sp.name, sp.fec_id)
            
            filings = F3X_Summary.objects.filter(fec_id = sp.fec_id)
            for filing in filings:
                print "Got F3x filing: %s - %s" % (filing.coverage_from_date, filing.coverage_to_date)
                this_file=filing.filing_number
                process_file(this_file, csvwriter)
                
        

        
        this_file=766953
        process_file(this_file, csvwriter)
        
        