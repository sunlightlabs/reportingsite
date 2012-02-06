from rebuckley.models import F3X_Summary, Contribution
from dateutil.parser import parse as dateparse


def clean_currency_field(currency_string):
    """ We return a string here; python 2.6 can't convert a float to a decimal, but can convert a string. """
    cs = currency_string.replace("$","")
    cs= cs.replace(",","")
    if (cs==''):
        cs='0'
    return cs
    
def process_summary_line(field_array, filing_number):
    form_type = field_array[0]
    amended = False
    if (form_type == 'F3XA'):
        amended=True
        print "*** Amended filing\n"
    committee_id = field_array[1][0:9]
    committee_name = field_array[2]
    address_change = field_array[3]
    street_1 = field_array[4]
    street_2 = field_array[5]
    city = field_array[6]
    state = field_array[7]
    zip = field_array[8]

    #print "\ncommittee: %s address_change: %s address: %s %s %s %s %s"  % (committee_name, address_change, street_1, street_2, city, state, zip)

    coverage_from_date = field_array[13]
    coverage_to_date = field_array[14]

    #print "Form covers %s - %s " % (coverage_from_date, coverage_to_date)

    coh_begin = field_array[22]
    total_receipts = field_array[23]
    total_disbursements = field_array[25]
    coh_close = field_array[26]
    itemized = field_array[80]
    unitemized = field_array[81]
    #print "\tCash on hand beginning: %s\n\t+total receipts %s ( = itemized: %s + unitemized: %s)\n\t-total_disbursements %s\n\t=Cash on hand close %s" % (coh_begin, total_receipts, itemized, unitemized, total_disbursements, coh_close)
    
    # enter the line: 
    try:
        F3X_Summary.objects.get(filing_number=filing_number)
    
    except F3X_Summary.DoesNotExist:
        print "Creating F3X_Summary from filing number: %s" % (filing_number)
        f3 = F3X_Summary.objects.create(
            filing_number=filing_number, 
            amended=amended, 
            committee_name=committee_name,
            fec_id=committee_id,
            address_change=address_change,
            street_1=street_1,
            street_2=street_2,
            city=city,
            state=state,
            zip=zip, 
            coverage_from_date=dateparse(coverage_from_date),
            coverage_to_date=dateparse(coverage_to_date),
            coh_begin=clean_currency_field(coh_begin),
            total_receipts=clean_currency_field(total_receipts),
            total_disbursements=clean_currency_field(total_disbursements),
            coh_close=clean_currency_field(coh_close),
            itemized=clean_currency_field(itemized),
            unitemized=clean_currency_field(unitemized)
            )
        f3.save()
            


def process_contrib_line(fields, filing_number, amended):
    """Process a line 11A1 contribution"""
    line_type = fields[0]
    committee_id = fields[1][0:9]
    transaction_id = fields[2][0:32]
    back_ref_tran_id = fields[3][0:32]
    back_ref_sked_name = fields[4][0:32]
    entity_type = fields[5]
    
    #print "committee %s \n transaction id: %s back_ref_tran_id: %s back_ref_sked_name: %s entity_type: %s" % (committee_id, transaction_id, back_ref_tran_id, back_ref_sked_name, entity_type)
    
    contrib_org = fields[6][0:200]
    contrib_last = fields[7][0:30]
    contrib_first = fields[8][0:20]
    contrib_middle = fields[9][0:20]
    contrib_prefix = fields[10][0:10]
    # suffix appears broken, ignore
    contrib_suffix = fields[11][0:10]
    contrib_street_1 = fields[12][0:34]
    contrib_street_2 = fields[13][0:34]
    contrib_city = fields[14][0:30]
    contrib_state = fields[15][0:2]
    contrib_zip = fields[16][0:9]
    contrib_date = fields[19]
    contrib_amt = fields[20]
    contrib_agg = fields[21]
    contrib_purpose = fields[22][0:100]
    contrib_employer = fields[23][0:37]
    contrib_occupation = fields[24][0:37]
    memo_agg_item = fields[42]
    memo_text_descript = fields[43]
    # "Reference to SI or SL system code that identifies the Account"
    s_ref = fields[43]
    
    #print "org: %s name: %s %s %s '%s' address: %s %s %s %s %s" % (contrib_org, contrib_prefix, contrib_first, contrib_middle, contrib_last, contrib_street_1, contrib_street_2, contrib_city, contrib_state, contrib_zip)
    #print "Amt: $%s, date %s, purpose: %s employer: %s, occupation: %s" % (contrib_amt, contrib_date, contrib_purpose, contrib_employer, contrib_occupation)
    
    # enter the data:
    
    try: 
        Contribution.objects.get(filing_number=filing_number,transaction_id=transaction_id)
    except Contribution.DoesNotExist:
        #print "Creating contrib from filing number: %s transaction_id: %s" % (filing_number, transaction_id)
        c = Contribution.objects.create(
            line_type=line_type.upper(),
            from_amended_filing=amended,
            fec_committeeid = committee_id,
            filing_number=filing_number,
            transaction_id=transaction_id,
            back_ref_tran_id=back_ref_tran_id,
            back_ref_sked_name=back_ref_sked_name,
            entity_type=entity_type,
            contrib_org=contrib_org,
            contrib_last=contrib_last,
            contrib_first=contrib_first,
            contrib_middle=contrib_middle,
            contrib_prefix=contrib_prefix,
            contrib_suffix=contrib_suffix,
            contrib_street_1=contrib_street_1,
            contrib_street_2=contrib_street_2,
            contrib_city=contrib_city,
            contrib_state=contrib_state,
            contrib_zip=contrib_zip,
            contrib_date=dateparse(contrib_date),
            contrib_amt=clean_currency_field(contrib_amt),
            contrib_agg=clean_currency_field(contrib_agg),
            contrib_purpose=contrib_purpose,
            contrib_employer=contrib_employer,
            contrib_occupation=contrib_occupation,
            memo_agg_item=memo_agg_item,
            memo_text_descript=memo_text_descript
        )
        c.save()
   
def enter_form(complete_file_text, filing_number):
    delimiter = chr(28)
    linecount = 0
    amended = False
    
    for line in complete_file_text.split("\n"):
        linecount+=1
        #print "Line is %s" % line
        
    # kill off the new lines 
        line = line.replace("\n","") 
        line = line.replace("\r","")

        # remove double quotes:
        line = line.replace('"','')
        
        fields = line.split(delimiter)
        # sometimes they lowercase the type
        line_type = fields[0].upper()
        
        if (linecount==1): 
            #print "'header line': %s" % fields
            #print "Verifying header version" 
            # disabling -- will this break on 7.0 ? 
            #assert (fields[2].strip()=="8.0")            
            pass
            
        if (linecount==2):
            form_type = fields[0]
            if (form_type == 'F3XA'):
                amended=True
            if (amended):
                print "*** Amended filing\n"
            process_summary_line(fields, filing_number)           
        
        if (linecount > 2):
            # Is it a sked 11 A1, B, or C line, or a line 15 
            if (line_type == 'SA11AI' or line_type == 'SA11B' or line_type == 'SA11C' or line_type == 'SA15'):
                process_contrib_line(fields, filing_number, amended)