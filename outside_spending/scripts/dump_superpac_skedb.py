import sys

from django.core.management import setup_environ
sys.path.append('/Users/jfenton/reporting/reportingsitenew/reportingsite')
sys.path.append('/projects/reporting/src/reportingsite')

import settings
setup_environ(settings)


from outside_spending.form_parser import form_parser
from outside_spending.filing import filing
from outside_spending.models import Committee_Overlay, F3X_Summary

from dateutil.parser import parse as dateparse

import csv

from name_cleaver import OrganizationNameCleaver

dumpfilename = "superpac_skedb_1024.csv"
outfile = open(dumpfilename, 'w')

fp = form_parser()


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
            #print "in filing: %s" % filingnum
            parsed_line = fp.parse_form_line(row, version)
            orgname = parsed_line['payee_organization_name'].replace('"','')
            
            parsed_line['orgname_parsed']=str(OrganizationNameCleaver(orgname).parse())
            parsed_line['orgname_kernel']=str(OrganizationNameCleaver(orgname).parse().kernel())
            parsed_line['orgname_expand']=str(OrganizationNameCleaver(orgname).parse().expand())
            
            #map_parsed_line(parsed_line)
            csvwriter.writerow(parsed_line)


field_list = ['filer_committee_id_number', 'committee_name' ,'form_type', 'transaction_id_number', 'expenditure_amount', 'expenditure_date', 'entity_type',  'payee_first_name', 'payee_last_name', 'payee_organization_name', 'orgname_parsed', 'orgname_kernel', 'orgname_expand','payee_street_1', 'payee_street_2', 'payee_city', 'filer_committee_id_number', 'expenditure_purpose_descrip', 'category_code', 'beneficiary_committee_name', 'beneficiary_committee_fec_id', 'conduit_name', 'conduit_city', 'conduit_state', 'memo_code', 'refund_or_disposal_of_excess', 'back_reference_tran_id_number', 'back_reference_sched_name']

#field_list = ['form_type', 'entity_type', 'contributor_name', 'contributor_organization_name','contribution_aggregate', 'contribution_amount', 'contribution_date', 'contributor_employer', 'contributor_occupation', 'contributor_first_name', 'contributor_middle_name', 'contributor_last_name', 'contributor_suffix', 'contributor_street_1', 'contributor_street_2', 'contributor_city', 'contributor_state', 'contributor_zip', 'election_code']


outfile = open(dumpfilename, 'w')
header = ''
for i in field_list:
    header = header + i + ", "
outfile.write(header + "\n")
csvwriter = csv.DictWriter(outfile, field_list, restval='', extrasaction='ignore')

superpac_ids = Committee_Overlay.objects.filter(is_superpac=True).values('fec_id').distinct()

for sp in superpac_ids:
    this_id = sp['fec_id']
    filings = F3X_Summary.objects.filter(fec_id=this_id, superceded_by_amendment=False)
    for afiling in filings:
        thisfilenum = afiling.filing_number
        print "Processing %s %s" % (this_id, afiling.filing_number)
        process_file(thisfilenum, csvwriter)