# 2014

import csv
import datetime

from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, render_to_response
# in 1.3 there's django.shortcuts.render . D'oh!
from django.http import HttpResponse, Http404
from django.db.models import Sum, Min
from django.db.models import Q
from django.contrib.localflavor.us.us_states import STATE_CHOICES

from django.template import RequestContext, loader

from fec_alerts.models import Filing_Scrape_Time, new_filing, newCommittee
from outside_spending_2014.models import (Scrape_Time, Contribution, Expenditure, 
                                     Committee, Candidate,
                                     Committee_Overlay, Candidate_Overlay,
                                     Pac_Candidate, Electioneering_93,
                                     Race_Aggregate, State_Aggregate,
                                     President_State_Pac_Aggregate)
from outside_spending_2014.utils.json_helpers import render_to_json
from outside_spending_2014.utils.chart_helpers import summarize_monthly

from settings import CSV_EXPORT_DIR

CACHE_TIME = 60 * 15
STATE_CHOICES = dict(STATE_CHOICES)


try:
    most_recent_scrape=Scrape_Time.objects.all().order_by('-run_time')[0]
    data_disclaimer = """ These files are preliminary and current through %s but we cannot guarantee their accuracy. For more information, see: http://reporting.sunlightfoundation.com/super-pac/data/about/2012-june-update/ Please note that contributions in these files are as of the most recent filing deadline. Independent expenditures are not comparable to the itemized disbursements found in PAC's year-end reports. For more on independent expenditures see here: http://www.fec.gov/pages/brochures/indexp.shtml """ % (most_recent_scrape.run_time)
    hybrid_superpac_disclaimer ="\"Hybrid\" super PACs--committees that have separate accounts for \"hard\" and \"soft\" money, are not included. For a list of these committees, see <a href=\"http://www.fec.gov/press/press2011/2012PoliticalCommitteeswithNon-ContributionAccounts.shtml\">here</a>."
    electioneering_details="""<a target="_new" href="http://www.fec.gov/pages/brochures/electioneering.shtml">Electioneering communications</a>  are broadcast communications not otherwise
    reported as independent expenditures. Electioneering communication
    reports do not state whether the communication was in support of or in
    opposition to the candidate, and they sometimes refer to multiple
    candidates."""
except IndexError:
    most_recent_scrape = None

expenditure_file_description = """ This file contains all schedule E transactions reported electronically. Filers are generally required to report these transactions twice: within 24-hours, and then again in a monthly/quarterly report. The numbers reported on 24-hour reports are only used when monthly reports covering that time period are not available."""

contribution_file_description = """ This file contains a wider range of receipt types than those listed on the web pages. Specifically, contributions (11AI, 11B, and 11C) ; Transfers through affiliates (SA12), Loan repayments received (SA14); Offsets to operating expenses (SA15); Refunds of contributions made to Federal Candidates and Other Political Committees and (SA17) other Federal Receipts."""


organizational_file_description = """ This file contains contributions (11AI, 11B, and 11C) and offsets to operating expenses (SA15)."""


def write_csv_to_file(file_description, local_file, fields, rows):
    local_response = open(local_file, 'w')
    writer = csv.writer(local_response)
    writer.writerow([data_disclaimer])
    writer.writerow([file_description])
    writer.writerow(fields)
    for row in rows:
        writer.writerow(row)

def generic_csv(file_description, filename, fields, rows):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    writer = csv.writer(response)
    writer.writerow([data_disclaimer])
    writer.writerow([file_description])
    writer.writerow(fields)
    for row in rows:
        writer.writerow(row)

    return response

def generic_csv_headless(filename, fields, rows):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    writer = csv.writer(response)
    writer.writerow(fields)
    for row in rows:
        writer.writerow(row)

    return response
    
def make_expenditure_list(expenditure_queryset):
    """ Make a list of expenditures; deal with possible null candidates/committees"""
    rows = []
    for ie in expenditure_queryset:
        committee_name = ""
        committee_fec_id = ""
        superpac_status=""
        hybrid_status=""
        
        if ie.committee:
            committee_name = ie.committee.name
            committee_fec_id = ie.committee.fec_id
            superpac_status=ie.committee.superpac_status()
            hybrid_status=ie.committee.hybrid_status()
        else:
            committee_name = ie.committee_name
            committee_fec_id = ie.raw_committee_id     
        
        candidate_party=""
        candidate_office = ""
        candidate_district=""
        candidate_state=""
        candidate_fec_id=""
        
        if ie.candidate:
            candidate_fec_id = ie.candidate.fec_id
            candidate_party = ie.candidate.party
            candidate_office = ie.candidate.office
            candidate_district=ie.candidate.district
            candidate_state=ie.candidate.state()
        else:
            candidate_fec_id = ie.raw_candidate_id
            candidate_party = ie.candidate_party_affiliation
            candidate_office = ie.office
            candidate_district=ie.district
            
        rows.append([committee_name, committee_fec_id, superpac_status, ie.election_type, ie.candidate_name, ie.support_or_oppose(), candidate_fec_id, candidate_party, candidate_office, candidate_district, candidate_state, ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number ])
        
    return rows

def expenditure_csv(request, cycle, committee_id):
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id, cycle=cycle)
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(committee=committee).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = committee.slug + "_expenditures.csv"
    return generic_csv(expenditure_file_description, file_name, fields, rows) 

def all_expenditures_csv(request, cycle):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(cycle=cycle, superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name =  "all_expenditures-%s.csv" % (cycle)
            
    return generic_csv(expenditure_file_description, file_name, fields, rows)  
    
def all_expenditures_csv_to_file(cycle):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(cycle=cycle, superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    
    file_name =  "%s/all_expenditures-%s.csv" % (CSV_EXPORT_DIR, cycle)

    write_csv_to_file(expenditure_file_description, file_name, fields, rows)
   

def expenditure_csv_state(request, cycle, state):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(state=state, cycle=cycle).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = state + "_expenditures_" + str(cycle) +".csv"
    return generic_csv(expenditure_file_description, file_name, fields, rows)    


def expenditure_csv_race(request, cycle, office, state, district):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(office=office, cycle=cycle).filter(superceded_by_amendment=False)
    if (office in ('H', 'S')):
        expenditures = expenditures.filter(candidate__state_race=state)
    if (office == 'H'):
        expenditures = expenditures.filter(candidate__district=district)    

    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = str(cycle) + "_" + office + "_" + state + "_" + district + "_expenditures.csv"
    return generic_csv(expenditure_file_description, file_name, fields, rows)

def contribs_csv(request, cycle, committee_id):                            
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id, cycle=cycle)
    contributions = Contribution.objects.filter(fec_committeeid=committee_id, superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA14', 'SA15', 'SA16', 'SA17'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC','Transaction ID', 'Filing Number']
    rows = []
    file_name = committee.slug + "_donors_" + str(cycle) + ".csv"

    for c in contributions:
        rows.append([c.contrib_source(), committee.name, committee_id, c.contrib_org, c.contrib_last, c.contrib_first, c.contrib_city, c.contrib_state, c.contrib_occupation, c.contrib_employer, c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number])
    return generic_csv(contribution_file_description, file_name, fields, rows)

def organizational_contribs_csv(request, cycle):

    contributions = Contribution.objects.select_related("committee", "candidate").filter(committee__isnull=False, superceded_by_amendment=False, cycle=cycle).exclude(contrib_org='').filter(line_type__in=['SA11AI', 'SA15'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'PAC political orientation','Donating organization', 'Donor street 1',  'Donor street 2', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC','Transaction ID', 'Filing Number', 'memo', 'memo text description']
    rows = []
    file_name = "organizational_donors_%s.csv" % (str(cycle))

    for c in contributions:
        rows.append([c.contrib_source(), c.committee.name, c.committee.fec_id, c.committee.political_orientation, c.contrib_org, c.contrib_street_1, c.contrib_street_2, c.contrib_city, c.contrib_state, c.contrib_occupation, c.contrib_employer, c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number, c.memo_agg_item, c.memo_text_descript])
    return generic_csv(organizational_file_description, file_name, fields, rows)
    
    

def state_contribs_csv(request, cycle, state):                            
    contributions = Contribution.objects.filter(contrib_state=state.upper(), superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA14', 'SA15', 'SA16', 'SA17'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = state + "_donors_" + str(cycle) + ".csv"

    for c in contributions:
        
        name = ''
        if (c.committee):
            name = c.committee.name
            
        rows.append([ c.contrib_source(), name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number])
    return generic_csv(contribution_file_description, file_name, fields, rows)        


def all_contribs_csv(request, cycle):                            
    contributions = Contribution.objects.filter(superceded_by_amendment=False, cycle=cycle, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA14', 'SA15', 'SA16', 'SA17'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = "all_donors.csv"

    for c in contributions:
        name = ''
        if (c.committee):
            name = c.committee.name

        rows.append([ c.contrib_source(), name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number])
    return generic_csv(contribution_file_description, file_name, fields, rows)
    
def all_contribs_csv_to_file(cycle):                            
    contributions = Contribution.objects.filter(superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA14', 'SA15', 'SA16', 'SA17'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = "all_donors_%s.csv" % (cycle)

    for c in contributions:
        name = ''
        if (c.committee):
            name = c.committee.name

        rows.append([ c.contrib_source(), name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number])
    
    file_name =  "%s/all_contribs-%s.csv" % (CSV_EXPORT_DIR, cycle)

    write_csv_to_file(contribution_file_description, file_name, fields, rows)


def electioneering_csv(request,cycle):
    line93s = Electioneering_93.objects.filter(superceded_by_amendment=False, cycle=cycle)
    fields = ['Transaction ID', 'Filing Number', 'Is amended', 'Name', 'Committee ID', 'Amount', 'Date', 'Payee', 'Purpose', 'Target names', 'Target ids']
    rows = []
    for l93 in line93s:
        target_list = []
        target_id_list = []
        for target in l93.target.all():
            candidate = target.candidate
            if candidate:
                candidate_name = "%s %s %s" % (candidate.fec_name, candidate.display_party(), candidate.race()) 
                target_id_list.append(candidate.fec_id)
                target_list.append(candidate_name)
            else:
                # If we haven't id'ed the candidate, use the raw text provided in the line 94 entry
                alt_name = "%s (%s)" % (target.can_name.upper(), target.can_state)
                target_list.append(alt_name)
                target_id_list.append(target.can_id)

        names = ";".join(target_list)
        ids = ";".join(target_id_list)
        rows.append([l93.transaction_id, l93.filing_number, l93.amnd_ind, l93.spe_nam, l93.fec_id, l93.exp_amo, l93.exp_date, l93.payee, l93.purpose, names, ids])
    file_name = "electioneering-%s.csv" % (cycle)
    info_row = "This is a summary of electioneering expenses. Because electioneering can target multiple candidates their names and ids are grouped together in the Target Names and Target Ids field. Electioneering groups do not disclose whether their ads support or oppose the ad targets. Candidate ids are missing for filings that omitted them."
    return generic_csv(info_row, file_name, fields, rows)
    
    
def committee_summary_public(request, cycle):
    committees = Committee_Overlay.objects.filter(cycle=cyle).filter( Q(is_superpac=True)|Q(total_indy_expenditures__gt=0) |Q(total_electioneering__gt=0)).select_related('committee_master_record')
    
    fields = ['Name', 'Committee ID', 'Is super pac', 'Party', 'Treasurer', 'Street_1', 'Street_2', 'City', 'ZIP code', 'state', 'connected_org_name', 'interest group category', 'committee type', 'designation', 'Filing frequency', 'Total contributions', 'Total unitemized contributions', 'cash on hand', 'last report date', 'total IEs', 'IEs support dems', 'IEs oppose dems', 'IEs support reps', 'IEs oppose reps', 'tax status']
    
    rows = []
    file_name = "committee_summary_.csv" % (cycle)
    
    
    for c in committees:
        
        interest_group_cat, ctype, designation, state = None, None, None, None
        if c.committee_master_record:
            interest_group_cat = c.committee_master_record.interest_group_cat
            ctype = c.display_type()
            designation = c.committee_master_record.designation
            state = c.committee_master_record.state_race

        rows.append([c.name, c.fec_id, c.superpac_status(), c.party, c.treasurer, c.street_1, c.street_2, c.city, c.zip_code, state, c.connected_org_name, interest_group_cat, ctype, designation, c.filing_frequency_text(), c.total_contributions, c.total_unitemized, c.cash_on_hand, c.cash_on_hand_date, c.total_indy_expenditures, c.ie_support_dems, c.ie_oppose_dems, c.ie_support_reps, c.ie_oppose_reps, c.org_status])
    return generic_csv("This is a summary of all groups that have made independent expenditures, are super PACs, or have made electioneering communications. Note that some groups may appear twice because they have multiple FEC identification numbers", file_name, fields, rows)
    
def superpac_political_orientation(request, cycle):
    committees = Committee_Overlay.objects.filter(cycle=cycle).filter( Q(is_superpac=True)).select_related('committee_master_record')

    fields = ['Name', 'Committee ID', 'Treasurer', 'Street_1', 'Street_2', 'City', 'ZIP code', 'state', 'Connected Org Name', 'Political Orientation', 'Filing frequency', 'Total receipts (includes both itemized and unitemized contributions)', 'Total unitemized contributions', 'cash on hand', 'last report date', 'total IEs', 'IEs support dems', 'IEs oppose dems', 'IEs support reps', 'IEs oppose reps']

    rows = []
    file_name = "committee_summary_%s.csv" % (cycle)


    for c in committees:

        interest_group_cat, ctype, designation, state = None, None, None, None
        if c.committee_master_record:
            interest_group_cat = c.committee_master_record.interest_group_cat
            ctype = c.display_type()
            designation = c.committee_master_record.designation
            state = c.committee_master_record.state_race

        rows.append([c.name, c.fec_id, c.treasurer, c.street_1, c.street_2, c.city, c.zip_code, state, c.connected_org_name, c.display_political_orientation(), c.filing_frequency_text(), c.total_contributions, c.total_unitemized, c.cash_on_hand, c.cash_on_hand_date, c.total_indy_expenditures, c.ie_support_dems, c.ie_oppose_dems, c.ie_support_reps, c.ie_oppose_reps])
    return generic_csv("This file contains a listing of all super PACs and the political affiliation Sunlight has assigned to them", file_name, fields, rows)    

def committee_summary_private(request, cycle):
    committees = Committee_Overlay.objects.filter(cycle=cycle).filter( Q(is_superpac=True)|Q(total_indy_expenditures__gt=0)|Q(total_electioneering__gt=0) ).select_related('committee_master_record')

    fields = ['Name', 'Committee ID', 'Is super pac', 'Party', 'Treasurer', 'Street_1', 'Street_2', 'City', 'ZIP code', 'state', 'connected_org_name', 'interest group category', 'committee type', 'designation', 'Filing frequency', 'Total contributions', 'Total unitemized contributions', 'cash on hand', 'last report date', 'total IEs', 'IEs support dems', 'IEs oppose dems', 'IEs support reps', 'IEs oppose reps', 'tax status', 'political_orientation', 'political orientation verified']

    rows = []
    file_name = "committee_summary_details_%s.csv" % (cycle)


    for c in committees:

        interest_group_cat, ctype, designation, state = None, None, None, None
        if c.committee_master_record:
            interest_group_cat = c.committee_master_record.interest_group_cat
            ctype = c.display_type()
            designation = c.committee_master_record.designation
            state = c.committee_master_record.state_race

        rows.append([c.name, c.fec_id, c.superpac_status(), c.party, c.treasurer, c.street_1, c.street_2, c.city, c.zip_code, state, c.connected_org_name, interest_group_cat, ctype, designation, c.filing_frequency_text(), c.total_contributions, c.total_unitemized, c.cash_on_hand, c.cash_on_hand_date, c.total_indy_expenditures, c.ie_support_dems, c.ie_oppose_dems, c.ie_support_reps, c.ie_oppose_reps, c.org_status, c.political_orientation, c.political_orientation_verified])
    return generic_csv("Summary of all groups that have made IE's or are a super PAC", file_name, fields, rows)    


@cache_page(CACHE_TIME)
def all_superpacs(request, cycle):
    year_start = int(cycle)-1
    explanatory_text = "This table shows all independent expenditure-only committees--better known as super PACs--that have spent at least $10,000 since the beginning of %s. The totals, listed above, are for all super PACs. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site. For the much longer list of <a href='/outside-spenders/%s/super-pacs/complete-list/'>all superpacs</a> click <a href='/outside-spenders/%s/super-pacs/complete-list/'>here</a>. Also see the list of <a href='/fec-alerts/new-superpacs/'>new superpacs</a> and <a href='/fec-alerts/new-committees/'>all new committees</a>." % (year_start, cycle, cycle)

    all_superpacs = Committee_Overlay.objects.filter(is_superpac=True, cycle=cycle)

    totals = all_superpacs.aggregate(support_dems=Sum('ie_support_dems'), oppose_dems=Sum('ie_oppose_dems'), oppose_reps=Sum('ie_oppose_reps'), support_reps=Sum('ie_support_reps'), total=Sum('total_indy_expenditures'), total_contribs=Sum('total_contributions'))
    totals = dict([(k, v or 0) for (k, v) in totals.items()])

    total_amt = totals['total']
    if total_amt is None or total_amt == 0:
        neg_percent = 0
        positive_percent = 0
    else:
        neg_percent = 100*(totals['oppose_dems']+totals['oppose_reps'])/totals['total']
        positive_percent = 100*(totals['support_dems']+totals['support_reps'])/totals['total']



    superpacs = all_superpacs.filter(is_superpac=True, cycle=cycle).filter(Q(total_indy_expenditures__gte=10000))
    data_dict = {'explanatory_text':explanatory_text, 
    'superpacs':superpacs, 
    'total_amt':total_amt, 
    'total_contribs':totals['total_contribs'],
    'neg_percent':neg_percent,
    'pos_percent':positive_percent,
    'cycle':cycle,
    }
    return render_to_response('outside_spending_2014/superpac_list.html',data_dict)
    
    
@cache_page(CACHE_TIME)                            
def committee_detail(request,cycle, committee_id):
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id, cycle=cycle)
    expenditures = Expenditure.objects.filter(committee=committee).filter(superceded_by_amendment=False).select_related('committee', 'candidate')
    contributions = Contribution.objects.filter(fec_committeeid=committee_id, superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA15'])
    candidates_supported = Pac_Candidate.objects.filter(committee=committee)
    explanatory_text = "This table shows the overall total amount spent by this group supporting or opposing federal candidates in independent expenditures in the %s election cycle." % (cycle)
    explanatory_text_details = 'This table shows the independent expenditures of $10,000 or more made by this group supporting or opposing federal candidates in the %s election cycle. To view a more detailed file of all such spending, <a href=\"%s\">click here</a>.' % (cycle, committee.superpachackcsv())
    explanatory_text_contribs = 'This table shows all contributions, related PAC transfers and operating expense offsets made to this group during the %s campaign cycle, as of %s. Operating expense offsets are marked with an asterisk (*). To view a more detailed file of this spending, which includes all receipt types, <a href=\"%s\">click here</a>.' % (cycle, committee.cash_on_hand_date,committee.superpachackdonorscsv())
    

    display_expenditures = expenditures.filter(expenditure_amount__gte=10000)
    has_chart = False 

    return render_to_response('outside_spending_2014/committee_detail.html',
                            {'committee':committee, 
                            'expenditures':display_expenditures,
                            'contributions':contributions, 
                            'candidates':candidates_supported,
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details,
                            'explanatory_text_contribs':explanatory_text_contribs, 
                            'has_chart':has_chart, 
                            'cycle':cycle,
                            })
                            

@cache_page(CACHE_TIME)
def races(request, cycle):
    races = Race_Aggregate.objects.filter(cycle=cycle).exclude(district__isnull=True)
    explanatory_text = "This page shows independent expenditures made in the " + str(cycle) +" election cycle by race. Click on each race to see aggregate totals by candidate, and to get access to a downloadable file of all individual expenditures for this race. " 
    # We're not showing electioneering, so don't bother to show the docs.
    # + electioneering_details
    return render_to_response('outside_spending_2014/race_list.html',
                            {'races':races, 
                            'explanatory_text':explanatory_text,
                            'cycle':cycle,
                            })


@cache_page(CACHE_TIME)                            
def race_detail(request, cycle, office, state, district):
    race_aggregate = get_object_or_404(Race_Aggregate, office=office, state=state, district=district, cycle=cycle)
    candidate_pacs = Pac_Candidate.objects.filter(cycle=cycle, candidate__office=office, candidate__state_race=state, candidate__district=district)

    explanatory_text = "This table shows the total amount of independent expenditures each group made to support or oppose a candidate in this race. For a downloadable file of this information, <a href=\"/outside-spenders/%s/csv/race/expenditures/%s/%s/%s/\">click here</a>." % (cycle,office, state, district)
    race_name = None
    if (office=='P'):
        race_name = 'President'
    elif office == 'S':
        race_name = '%s (Senate)' % state
    else:
        race_name='%s-%s (House)' % (state, district.lstrip('0'))

    return render_to_response('outside_spending_2014/race_detail.html',
                            {'candidates':candidate_pacs, 
                            'explanatory_text':explanatory_text, 
                            'race_name':race_name,
                            'race_aggregate':race_aggregate, 
                            'ec_explanation':electioneering_details,
                            'cycle':cycle,
                            })
    

@cache_page(CACHE_TIME)                            
def candidates(request,cycle):
    candidates = Candidate_Overlay.objects.filter(total_expenditures__gte=10, cycle=cycle)
    explanatory_text= "This table lists all independent expenditures made to support or oppose federal candidates during the %s election cycle. Candidates not targeted are not included."
    return render_to_response('outside_spending_2014/candidate_list.html',
                            {'candidates':candidates, 
                            'explanatory_text':explanatory_text,
                            'cycle':cycle,
                            })
@cache_page(CACHE_TIME) 
def candidate_detail(request, cycle, candidate_id):
    candidate = Candidate_Overlay.objects.get(cycle=cycle, fec_id=candidate_id)
    explanatory_text= 'This is a list of all super PACs that have made independent expenditures supporting or opposing this candidate.'
    explanatory_text_details = 'This is a list of all independent expenditures of $10,000 or more made by any committee for or against this candidate.'
    superpacs = Pac_Candidate.objects.filter(cycle=cycle,candidate=candidate)
    expenditures = Expenditure.objects.filter(cycle=cycle,superceded_by_amendment=False, candidate=candidate, expenditure_amount__gte=10000).select_related("committee")


    return render_to_response('outside_spending_2014/candidate_detail.html',
                            {'candidate':candidate, 
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details,
                            'superpacs':superpacs,
                            'expenditures':expenditures,
                            'cycle':cycle,
                            })
                            
def states(request, cycle):
    states = State_Aggregate.objects.filter(cycle=cycle, total_ind_exp__gt=0)
    explanatory_text= "This table lists the sums of independent expenditures and electioneering communications reported to have been made in each state during the %s election cycle. The FEC does not require that general election spending in support of a president be designated to a particular state. Moreover, the state designation is sometimes omitted from reports where it should be included. Therefore, the totals on this page will not match overall totals found elsewhere on this site. For downloadable state-by-state files, see the <a href=\"/outside-spenders/%s/file-downloads/\">downloads page</a>."  % (cycle, cycle)
    return render_to_response('outside_spending_2014/state_list.html',
                            {'states':states, 
                            'explanatory_text':explanatory_text,
                            'cycle':cycle,
                            })                                                                                                        

def state_detail(request, cycle, state_abbreviation):

    try:
        state_name = STATE_CHOICES[state_abbreviation]
    except KeyError:
        raise Http404


    races = Race_Aggregate.objects.filter(cycle=cycle, state__iexact=state_abbreviation).exclude(district__isnull=True)
    this_state = State_Aggregate.objects.get(cycle=cycle, state=state_abbreviation)

    candidates = Candidate_Overlay.objects.filter(cycle=cycle, total_expenditures__gte=10, state_race__iexact=state_abbreviation)

    explanatory_text= 'For a downloadable .csv file of this information, <a href="/outside-spenders/%s/csv/state/expenditures/%s/">click here</a>.</p><p>This table lists the total of all independent expenditures and electioneering communications designated to this state during the %s election cycle by race. The FEC does not require that general election spending in support of a president be designated to a particular state. Moreover, the state designation is sometimes omitted from reports where it should be included.' % (cycle, state_abbreviation, cycle)
    return render_to_response('outside_spending_2014/state_detail.html',
                            {'races':races, 
                            'state_name':state_name,
                            'candidates':candidates,
                            'explanatory_text':explanatory_text,
                            'this_state':this_state,
                            'cycle':cycle,
                            })

@cache_page(CACHE_TIME)
def ies(request, cycle):
    # When there are more to show, limit it to recent ones only. 
    # today = datetime.date.today()
    # two_weeks_ago = today - datetime.timedelta(days=7)
    ies = Expenditure.objects.select_related("committee", "candidate").filter(cycle=cycle, superceded_by_amendment=False, expenditure_amount__gte=10000).order_by('-expenditure_date')
    explanatory_text= "This page shows independent expenditures made this cycle for $10,000 or more. See the <a href=\"http://assets.sunlightfoundation.com/reporting/FTUM-data-%s/all_expenditures-%s.csv\">complete file</a> of independent expenditures for amounts less than $10,000." % (cycle, cycle)
    return render_to_response('outside_spending_2014/expenditure_list.html',
                            {'ies':ies, 
                            'explanatory_text':explanatory_text,
                            'cycle':cycle,
                            })
                            
# there aren't any yet. 
@cache_page(CACHE_TIME)
def organizational_superpac_contribs(request, cycle):
    contribs = Contribution.objects.select_related("committee").filter(cycle=cycle, committee__isnull=False, superceded_by_amendment=False).exclude(contrib_org='').filter(line_type__in=['SA11AI', 'SA15'])


    total = contribs.aggregate(total=Sum('contrib_amt'))
    total_amt = total['total']

    explanatory_text= 'This is a list of all contributions to super PACs from organizations, including money received as operating expense offsets. These offsets, which are marked with an asterisk below, often include administrative overhead paid by a related organization, though sometimes include refund payments. This list does not include contributions from corporate--or any other--PACs. Also see a <a href="/outside-spending/noncommittees/">summary page of non-committees making independent expenditures</a>.'
    return render_to_response('outside_spending_2014/organizational_contribs.html',
                            {'contribs':contribs,
                            'total_amt':total_amt,
                            'explanatory_text':explanatory_text,
                            'cycle':cycle,
                            })


def search(request, cycle):
    query = request.GET.get('q')

    terms = None
    invalid_search = False
    num_results = 0
    has_committees = False
    has_candidates = False

    if not query:
        invalid_search = True
    if len(query)<4:
        invalid_search = True    
        committee_overlays = None
        committees = None
        has_committees = False
        candidate_overlays = None
        has_candidates = False
        candidates = None

    else:
        terms = query
        search_terms = terms.split(" ")

        # Hack to keep a search for "mitt" from matching every comMITTee
        for index,term in enumerate(search_terms):
            if term.upper()=='MITT':
                search_terms[index] = term + " "

        # Get committees we know about
        committee_overlays = Committee_Overlay.objects.filter(  Q(total_indy_expenditures__gt=0)|Q(is_superpac=True) ).select_related()
        for i in search_terms:
            committee_overlays = committee_overlays.filter(name__icontains=i)
        committee_overlays = committee_overlays.select_related()


        # we don't want to list a committee twice, so come up with a list to exclude later
        ids = committee_overlays.values('fec_id')
        id_list = []
        for this_id in ids:
            id_list.append(this_id['fec_id'])

        print id_list

        committees1 = Committee.objects.all()
        committees2 = Committee.objects.all()
        for i in search_terms:
            committees1 = committees1.filter(name__icontains=i)
            committees2 = committees2.filter(related_candidate__fec_name__icontains=i)

        committees = committees1 | committees2

        committees = committees.exclude(fec_id__in=id_list).select_related()

        if (len(committee_overlays) + len(committees) > 0):
            has_committees=True
            num_results = 1

        candidate_overlays = Candidate_Overlay.objects.filter(  Q(total_expenditures__gt=0) | Q(electioneering__gt=0))
        for i in search_terms:
            candidate_overlays = candidate_overlays.filter(fec_name__icontains=i)
        candidate_overlays = candidate_overlays.select_related()

        candidate_ids = candidate_overlays.values('fec_id')
        candidate_id_list = []
        for this_id in candidate_ids:
            candidate_id_list.append(this_id['fec_id'])
        print candidate_id_list

        candidates = Candidate.objects.all().exclude(fec_id__in=candidate_id_list)
        for i in search_terms: 
            candidates = candidates.filter(fec_name__icontains=i)
        candidates = candidates.select_related()


        if (len(candidate_overlays) + len(candidates) > 0):
            has_candidates = True


    return render_to_response('outside_spending_2014/search.html', {
                'terms':terms,
                'invalid_search':invalid_search, 
                'num_results':num_results,
                'committee_overlays':committee_overlays,
                'committees':committees,
                'has_committees':has_committees,
                'candidate_overlays':candidate_overlays,
                'has_candidates':has_candidates,
                'candidates':candidates,
                'cycle':cycle,
                })
            
@cache_page(CACHE_TIME)                            
def file_downloads(request, cycle):
    committees = Committee_Overlay.objects.filter(cycle=cycle,total_contributions__gte=1000).order_by('name')
    states = State_Aggregate.objects.filter(cycle=cycle,total_ind_exp__gt=0).order_by('state')
    races = Race_Aggregate.objects.filter(cycle=cycle,total_ind_exp__gt=0).order_by('state', 'office', 'district')

    return render_to_response('outside_spending_2014/file_downloads.html',
                            {'committees':committees, 
                            'states':states,
                            'races':races,
                            'cycle':cycle,
                            })
