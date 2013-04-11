
import re, os

from dateutil.parser import parse as dateparse
from datetime import date
from time import sleep

from django.core.management.base import BaseCommand, CommandError

from outside_spending_2014.form_parser import form_parser
from outside_spending_2014.filing import filing
from outside_spending_2014.models import Expenditure, F3X_Summary, Contribution
from outside_spending_2014.read_FEC_settings import CYCLE, CYCLE_START, CYCLE_END, LAST_CYCLE_END
from outside_spending_2014.management.commands.overlay_utils import *

# Ignore anything before this date.
epoch_start = dateparse(CYCLE_START)
epoch_end = dateparse(CYCLE_END)
last_epoch_end = dateparse(LAST_CYCLE_END)

def clean_currency_field(currency_string):
    """ We return a string here; python 2.6 can't convert a float to a decimal, but can convert a string. """
    cs = currency_string.replace("$","")
    cs= cs.replace(",","")
    if (cs==''):
        cs='0'
    return cs

def process_F24(f24_to_process, fp):

    filingnum = f24_to_process
    #processtime = f24_to_process.process_time
    

    f1 = filing(filingnum, True, True)
    f1.download()
    formtype = f1.get_form_type()
    version = f1.version

    print "Got form number %s - type=%s version=%s is_amended: %s" % (f1.filing_number, formtype, version, f1.is_amendment)

    if not (formtype == 'F24' or formtype == 'F5'):
        print "Not an F24 or an F5!!"
        return None
    
        

    firstrow = fp.parse_form_line(f1.get_first_row(), version)    
    #print firstrow
    committee_id = firstrow['filer_committee_id_number']
    committee_name = ''
    try:
        committee_name = firstrow['committee_name']
    except KeyError:
        pass
    
    all_ie_spending = []
    
    schedule_e_lines = f1.get_rows('SE')
    schedule_57_lines = f1.get_rows('F57')
    
    print "sked e: %s sked 57 %s" % (len(schedule_e_lines), len(schedule_57_lines))

    all_ie_spending.extend(schedule_e_lines)
    all_ie_spending.extend(schedule_57_lines)
    
    
    headers = f1.get_headers()
    is_amendment = headers['is_amendment']
    
    original=None
    if (is_amendment):
        original=headers['filing_amended']    
        
    for e_line in all_ie_spending:
        thisrow = fp.parse_form_line(e_line, version)        
        print "\nGot sked E line: %s\n" % (thisrow)
        transaction_id = thisrow['transaction_id_number']
        
        # don't save it if it's too early
        expenditure_date = dateparse(thisrow['expenditure_date'])
        if expenditure_date < epoch_start or expenditure_date > epoch_end:
            return
        
        print "Looking for filing %s transaction number %s" % (filingnum, transaction_id)
        
        # look for this as an existing transaction in the db: 
        try:
            Expenditure.objects.get(filing_number=filingnum, transaction_id=transaction_id)
        except Expenditure.DoesNotExist:
            
            
            ## Look for a F3X that already covers this period. This is a rare occurrence but it has happened some (most notably with Gingrich's super PAC). Basically, they amend an F24 long after they filed an F3X for the period. When this happens, favor the F3X that is filed, and skip the F24. This isn't really a concern for F5's.
            if (formtype == 'F24'):
                
                preexisting_f3xs = F3X_Summary.objects.filter(superceded_by_amendment=False, fec_id=committee_id, coverage_from_date__lte=expenditure_date, coverage_to_date__gte=expenditure_date)
                if len(preexisting_f3xs) > 0:
                    # This transactions already been entered on an F3X, so skip it. 
                    print "** Already covered in F3X ; skipping %s %s" % (committee_name, expenditure_date, )
                    continue
                
                
            
            
            this_candidate = get_or_create_candidate_overlay(thisrow['candidate_id_number'], CYCLE)
            this_committee = get_or_create_committee_overlay(committee_id, CYCLE)
            
            payee_name = ''
            if len(thisrow['payee_organization_name'])>3:
                payee_name = thisrow['payee_organization_name']
            else:
                payee_name = thisrow['payee_last_name'] + ", " + thisrow['payee_first_name'] 
                
            # older versions used candidate name--newer versions break it up. 
            candidate_name = ''
            try:
                candidate_name = thisrow['candidate_last_name'] + ", " + thisrow['candidate_first_name']
                
            except KeyError:
                candidate_name = thisrow['candidate_name']
                
            amendment_value = ''
            if is_amendment:
                amendment_value = 'A'
                
            memo_code = ''
            try:
                memo_code =thisrow['memo_code']
            except KeyError:
                pass
            
            memo_text_description=''
            try:
                memo_text_description=thisrow['memo_text_description']
            except KeyError:
                pass
            
            date_received = None    
            # sked 57 doesn't include receipt date--so use process time 
            try:
                date_received = dateparse(thisrow['date_signed'])
            except KeyError:
                pass
                #try:
                #    date_received=date(processtime.year,processtime.month,processtime.day)
                
                
            # apparently election codes can be blank
            election_code = ""
            try:
                election_code = thisrow['election_code'][0]
            except IndexError: 
                pass
                
            
            created = Expenditure.objects.create(
                cycle=CYCLE,
                image_number = 1,
                raw_committee_id = committee_id, 
                committee = this_committee, 
                payee = payee_name,
                expenditure_purpose = thisrow['expenditure_purpose_descrip'],
                expenditure_date =  expenditure_date,
                expenditure_amount = clean_currency_field(thisrow['expenditure_amount']),
                support_oppose = thisrow['support_oppose_code'],
                election_type = election_code,
                candidate_name = candidate_name,
                raw_candidate_id =  thisrow['candidate_id_number'].strip(),
                candidate = this_candidate,
                candidate_party_affiliation = None,
                office =  thisrow['candidate_office'],
                state =  thisrow['candidate_state'],
                district =  thisrow['candidate_district'],
                transaction_id = thisrow['transaction_id_number'],
                receipt_date =  date_received,
                filing_number =  filingnum,
                amendment =  amendment_value,
                race = ' ',
                pdf_url = ' ',
                committee_name =  committee_name,
                amends_filing=original,                
                amends_earlier_filing = is_amendment,
                #process_time = processtime,
                filing_source=formtype,
                memo_code = memo_code,
                memo_text_description=memo_text_description
            )
            
            
            # If it's an amendment, we need to mark earlier rows as being superceded by this amendment.
            
            
            if is_amendment:
                original_ies = Expenditure.objects.filter(filing_number=original)
                print "Writing amended original: %s %s" % (original, filingnum)
                for original_ie in original_ies:
                    original_ie.superceded_by_amendment=True
                    original_ie.amended_by = filingnum
                    original_ie.save()

                # Now find others that amend the same filing 
                earlier_amendments = Expenditure.objects.filter(amends_earlier_filing=True,amends_filing=original, filing_number__lt=filingnum)
                for earlier_amendment in earlier_amendments:
                    #print "** Handling prior amendment: %s %s" % (earlier_amendment.filing_number, header.filing_number)
                    earlier_amendment.superceded_by_amendment=True
                    earlier_amendment.amended_by = filingnum
                    earlier_amendment.save()


def process_F3X(f3x_to_process, fp):

    filingnum = f3x_to_process
    #processtime = f3x_to_process.process_time

    f1 = filing(filingnum, True, True)
    f1.download()

    formtype = f1.get_form_type()
    version = f1.version

    #print "Got form number %s - type=%s version=%s is_amended: %s" % (f1.filing_number, formtype, version, f1.is_amendment)


    if not (formtype == 'F3X'):
        print "Not an F3X!!"
        return 0



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
        print "\nGot sked E line: %s\n" % (thisrow)
        transaction_id = thisrow['transaction_id_number']

        # look for this as an existing transaction in the db: 
        try:
            Expenditure.objects.get(filing_number=filingnum, transaction_id=transaction_id)
        except Expenditure.DoesNotExist:

            # short circuit this if it's before 1/1/2011
            expenditure_date = dateparse(thisrow['expenditure_date'])
            if expenditure_date < epoch_start or expenditure_date > epoch_end:
                return

            this_candidate = get_or_create_candidate_overlay(thisrow['candidate_id_number'], CYCLE)
            this_committee = get_or_create_committee_overlay(committee_id, CYCLE)

            payee_name = ''
            if len(thisrow['payee_organization_name'])>3:
                payee_name = thisrow['payee_organization_name']
            else:
                payee_name = thisrow['payee_last_name'] + ", " + thisrow['payee_first_name'] 

            # older versions used candidate name--newer versions break it up. 
            candidate_name = ''
            try:
                candidate_name = thisrow['candidate_last_name'] + ", " + thisrow['candidate_first_name']

            except KeyError:
                candidate_name = thisrow['candidate_name']

            amendment_value = ''
            if is_amendment:
                amendment_value = 'A'

            date_received = dateparse(thisrow['date_signed'])

            # apparently election codes can be blank
            election_code = ""
            try:
                election_code = thisrow['election_code'][0]
            except IndexError: 
                pass

            created = Expenditure.objects.create(
                cycle=CYCLE,
                image_number = 1,
                raw_committee_id = committee_id, 
                committee = this_committee, 
                payee = payee_name,
                expenditure_purpose = thisrow['expenditure_purpose_descrip'],
                expenditure_date =  expenditure_date,
                expenditure_amount = clean_currency_field(thisrow['expenditure_amount']),
                support_oppose = thisrow['support_oppose_code'],
                election_type = election_code,
                candidate_name = candidate_name,
                raw_candidate_id =  thisrow['candidate_id_number'].strip(),
                candidate = this_candidate,
                candidate_party_affiliation = None,
                office =  thisrow['candidate_office'],
                state =  thisrow['candidate_state'],
                district =  thisrow['candidate_district'],
                transaction_id = thisrow['transaction_id_number'],
                receipt_date =  date_received,
                filing_number =  filingnum,
                amendment =  amendment_value,
                race = ' ',
                pdf_url = ' ',
                committee_name =  committee_name,
                amends_filing=original,                
                amends_earlier_filing = is_amendment,
                #process_time = processtime,
                filing_source = 'F3X'
            )



    # If it's an amendment, we need to mark earlier rows as being superceded by this amendment.

    original_ies = Expenditure.objects.filter(filing_number=original)
    for original_ie in original_ies:
        print "Writing amended original: %s %s" % (original, filingnum)
        original_ie.superceded_by_amendment=True
        original_ie.amended_by = filingnum
        original_ie.save()

    # if this is an f3xa, we still need to mark f24's that were superceded by it's original as now being superceded by this f3x. Maybe we shouldda just deleted them? 

    # Now find others that amend the same filing 
    earlier_amendments = Expenditure.objects.filter(amends_earlier_filing=True,amends_filing=original, filing_number__lt=filingnum)
    for earlier_amendment in earlier_amendments:
        #print "** Handling prior amendment: %s %s" % (earlier_amendment.filing_number, header.filing_number)
        earlier_amendment.superceded_by_amendment=True
        earlier_amendment.amended_by = filingnum
        earlier_amendment.save()

    # now mark all F24s that occurrred during this time period as having been superceded. 

    #all_f24_ies = Expenditure.objects.filter()
    start_date = dateparse(firstrow['coverage_from_date'])
    end_date = dateparse(firstrow['coverage_through_date'])
    print "Looking for ie filings from %s to %s" % (start_date, end_date)  
    f24_ies = Expenditure.objects.filter(raw_committee_id=committee_id, filing_number__lt=filingnum, filing_source='F24', expenditure_date__gte=start_date, expenditure_date__lte=end_date)
    for f24 in f24_ies:
        print "Handling superceded f24 expenditure: %s %s" % (f24.filing_number, f24.transaction_id)
        f24.superceded_by_amendment=True
        f24.superceded_by_f3x = True
        f24.superceding_f3x = filingnum
        f24.save()


    return len(schedule_e_lines)
    


# the rest is for processing contrib stuff. 

def process_contrib_line(values_dict, is_amendment, original, filing_number, committee_obj, committee_name):
    obj, created = Contribution.objects.get_or_create(filing_number=filing_number, transaction_id=values_dict['transaction_id'],
        defaults={
            "line_type": values_dict['form_type'],
            "from_amended_filing":is_amendment,
            "committee":committee_obj,
            "committee_name":committee_name,
            "fec_committeeid":values_dict['filer_committee_id_number'],
            "filing_number":filing_number,
            "back_ref_tran_id":values_dict['back_reference_tran_id_number'],
            "back_ref_sked_name":values_dict['back_reference_sched_name'],
            "entity_type":values_dict['entity_type'],
            "contrib_org":values_dict['contributor_organization_name'][:200],
            "contrib_last":values_dict['contributor_last_name'][:30],
            "contrib_first":values_dict['contributor_first_name'][:20],
            "contrib_middle":values_dict['contributor_middle_name'][:20],
            "contrib_prefix":values_dict['contributor_prefix'][:10],
            "contrib_suffix":values_dict['contributor_suffix'][:10],
            "contrib_street_1":values_dict['contributor_street_1'][:34],
            "contrib_street_2":values_dict['contributor_street_2'][:34],
            "contrib_city":values_dict['contributor_city'][:30],
            "contrib_state":values_dict['contributor_state'][:2],
            "contrib_zip":values_dict['contributor_zip'],
            "contrib_date":dateparse(values_dict['contribution_date']),
            "contrib_amt":clean_currency_field(values_dict['contribution_amount']),
            "contrib_agg":clean_currency_field(values_dict['contribution_aggregate']),
            "contrib_purpose":values_dict['contribution_purpose_descrip'],
            "contrib_employer":values_dict['contributor_employer'][:38],
            "contrib_occupation":values_dict['contributor_occupation'][:38],
            "memo_agg_item":values_dict['memo_code'][:100],
            "memo_text_descript":values_dict['memo_text_description'][:100]
        })

    # Now go through and mark earlier files as amendments, as appropriate                           
    if created:
        if is_amendment:
            original_contribs = Contribution.objects.filter(filing_number=original, superceded_by_amendment=False)
            for original_contrib in original_contribs:
                print "Writing amended original contrib: %s %s" % (original, original_contrib.filing_number)
                original_contrib.superceded_by_amendment=True
                original_contrib.amended_by = filing_number
                original_contrib.save()

            # Now find others that amend the same filing 
            earlier_amendments = Contribution.objects.filter(from_amended_filing=True,original=original, filing_number__lt=filing_number)
            for earlier_amendment in earlier_amendments:
                #print "** Handling prior amendment: %s %s" % (earlier_amendment.filing_number, header.filing_number)
                earlier_amendment.superceded_by_amendment=True
                earlier_amendment.amended_by = filing_number
                earlier_amendment.save()    



def process_summary_line(values_dict, is_amendment, original, filing_number):
    print "Processing summary %s" % (filing_number)
    # sometimes quote marks get in here. 
    values_dict['filer_committee_id_number'] = values_dict['filer_committee_id_number'].replace('"','')
    
    obj, created = F3X_Summary.objects.get_or_create(filing_number=filing_number,
    defaults={
        "amended":is_amendment,
        "fec_id":values_dict['filer_committee_id_number'].strip()[0:9],
        "committee_name":values_dict['committee_name'].strip(),
        "address_change":values_dict['change_of_address'][:1],
        "street_1":values_dict['street_1'],
        "street_2":values_dict['street_2'],
        "city":values_dict['city'],
        "state":values_dict['state'][:2],
        "zip":values_dict['zip'],
        "coverage_from_date":dateparse(values_dict['coverage_from_date']),
        "coverage_to_date":dateparse(values_dict['coverage_through_date']),
        "coh_begin":clean_currency_field(values_dict['col_a_cash_on_hand_beginning_period']),
        "total_receipts":clean_currency_field(values_dict['col_a_total_receipts']),
        "total_disbursements":clean_currency_field(values_dict['col_a_total_disbursements']),
        "coh_close":clean_currency_field(values_dict['col_a_cash_on_hand_close_of_period']),
        "itemized":clean_currency_field(values_dict['col_a_individuals_itemized']),
        "unitemized":clean_currency_field(values_dict['col_a_individuals_unitemized']),
        "debts_owed":clean_currency_field(values_dict['col_a_debts_by']), 
        "total_sched_e":clean_currency_field(values_dict['col_a_independent_expenditures']),        
        "ytd_total_receipts":clean_currency_field(values_dict['col_b_total_receipts']),   
        "ytd_total_disbursements":clean_currency_field(values_dict['col_b_total_disbursements']),   
        "ytd_sched_e":clean_currency_field(values_dict['col_b_independent_expenditures']),
        "amends_earlier_filing":is_amendment,
        "original":original
        })
        

    # Now go through and mark earlier files as amendments, as appropriate                           
    if created:
        if is_amendment:
            original_f3xs = F3X_Summary.objects.filter(filing_number=original)
            for original_f3x in original_f3xs:
                print "Writing amended original f3x: %s %s" % (original, original_f3x.filing_number)
                original_f3x.superceded_by_amendment=True
                original_f3x.amended_by = filing_number
                original_f3x.save()

            # Now find others that amend the same filing 
            earlier_amendments = F3X_Summary.objects.filter(amended=True,original=original, filing_number__lt=filing_number)
            for earlier_amendment in earlier_amendments:
                #print "** Handling prior amendment: %s %s" % (earlier_amendment.filing_number, header.filing_number)
                earlier_amendment.superceded_by_amendment=True
                earlier_amendment.amended_by = filing_number
                earlier_amendment.save()        

def process_F3X_contribs(filingnum, fp):


    f1 = filing(filingnum, True, True)
    f1.download()

    formtype = f1.get_form_type()
    version = f1.version

    print "Got form number %s - type=%s version=%s is_amended: %s" % (f1.filing_number, formtype, version, f1.is_amendment)


    if not (formtype == 'F3X'):
        print "Not an F24 or an F5!!"
        return 0

    firstrow = fp.parse_form_line(f1.get_first_row(), version) 

    # Ignore it unless it's the last report of the last cycle
    end_date = dateparse(firstrow['coverage_through_date'])
    
    
    if (end_date < last_epoch_end):
        return 0

    #print firstrow
    committee_id = firstrow['filer_committee_id_number']
    committee_name = firstrow['committee_name']

    print "id: %s committee: %s" % (committee_id, committee_name)


    headers = f1.get_headers()
    is_amendment = headers['is_amendment']

    original=None
    if (is_amendment):
       original=headers['filing_amended']    




    print "running summary: is_amendment: %s originial: %s, filingnum: %s " % (is_amendment, original, filingnum)
    process_summary_line(firstrow, is_amendment, original, filingnum)

    # we need the committee overlay object
    committee_overlay = get_or_create_committee_overlay(committee_id, CYCLE)
    committee_name = None
    if committee_overlay:
        committee_name = committee_overlay.name
    else:
        return 0

    # only enter contribs for super pacs
    if not committee_overlay.is_superpac:
        return 0    

    schedule_a_lines = f1.get_rows('SA')

    for a_line in schedule_a_lines:    
        thisrow = fp.parse_form_line(a_line, version)        
        print "\nGot sked A line: %s\n" % (thisrow)

        process_contrib_line(thisrow, is_amendment, original, filingnum, committee_overlay, committee_name)

    return len(schedule_a_lines)

""" Treat a monthly F5 as if it's a 24hour notice F5 -- just pull the contribs. Needed for American Future Fund, which to date has filed monthly forms but not 24-hour notices. """

def process_monthly_F5_contribs(filingnum, fp):
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
        if (parsed_line['report_type']=='24' or parsed_line['report_type']=='48'):
            # ignore reports that aren't 24 or 48
            print "This is a 24- or 48- hour notice form. Ignoring. "
            return
        else:
            process_F24(filingnum, fp)   
             
    else:
        print "Not an F5-- doing nothing."



""" Handle basic ie process files -- F3X, F5, F24"""    
def process_file(filingnum, fp):
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
    
    
    if (re.match('^F5', form) or re.match('^F24', form) or re.match('^F3X', form) ):
        
        if (re.match('^F5', form)):
            parsed_line = fp.parse_form_line(f1.get_first_row(), version)
            print "\n***%s:  %s - %s\n %s - %s" % (filingnum, parsed_line['report_code'], parsed_line['report_type'],  parsed_line['coverage_from_date'],  parsed_line['coverage_through_date'])
            if (parsed_line['report_type']!='24' and parsed_line['report_type']!='48'):
                # ignore reports that aren't 24 or 48
                print "Missing !!!!"
                return
            else:
                process_F24(filingnum, fp)
        
        if (re.match('^F24', form)):
            process_F24(filingnum, fp)
            
        if (re.match('^F3X', form)):     
            # are there any sked e lines ? we need to return this, and enter the contribs if there are. Enter contribs actually functions to add the summary line... 
            sked_e_linecount = process_F3X(filingnum, fp)
            print "Got sked e linecount of %s" % sked_e_linecount
            
            
            # only add contribs if there are sked e expenditures or its a superpac. If it's not a superpac, process_F3X_contribs won't add the sched A stuff.
            if (sked_e_linecount > 0):
                process_F3X_contribs(filingnum, fp)             
            else:
                committee_overlay = get_or_create_committee_overlay(filer_id, CYCLE)
                if committee_overlay:
                    if committee_overlay.is_superpac:
                        process_F3X_contribs(filingnum, fp) 
                    

