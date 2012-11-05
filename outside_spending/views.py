# Create your views here.
import csv
import datetime
import time

from django.views.decorators.cache import cache_page
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response, redirect
# in 1.3 there's django.shortcuts.render . D'oh!
from django.http import *
from django.db.models import Sum, Min
from django.db.models import Q
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.humanize.templatetags.humanize import intcomma
from outside_spending.models import Scrape_Time

STATE_CHOICES = dict(STATE_CHOICES)
most_recent_scrape=Scrape_Time.objects.all().order_by('-run_time')[0]

from outside_spending.models import *
from outside_spending.utils.json_helpers import render_to_json
from outside_spending.utils.chart_helpers import summarize_monthly

from settings import CSV_EXPORT_DIR
CACHE_TIME = 60 * 15


data_disclaimer = """ These files are preliminary and current through %s but we cannot guarantee their accuracy. For more information, see: http://reporting.sunlightfoundation.com/super-pac/data/about/2012-june-update/ Please note that contributions in these files are as of the most recent filing deadline. Independent expenditures are not comparable to the itemized disbursements found in PAC's year-end reports. For more on independent expenditures see here: http://www.fec.gov/pages/brochures/indexp.shtml """ % (most_recent_scrape.run_time)

hybrid_superpac_disclaimer ="\"Hybrid\" super PACs--committees that have separate accounts for \"hard\" and \"soft\" money, are not included. For a list of these committees, see <a href=\"http://www.fec.gov/press/press2011/2012PoliticalCommitteeswithNon-ContributionAccounts.shtml\">here</a>."

electioneering_details="""<a target="_new" href="http://www.fec.gov/pages/brochures/electioneering.shtml">Electioneering communications</a>  are broadcast communications not otherwise
reported as independent expenditures. Electioneering communication
reports do not state whether the communication was in support of or in
opposition to the candidate, and they sometimes refer to multiple
candidates. """


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
            
        rows.append([committee_name, committee_fec_id, superpac_status, ie.election_type, ie.candidate_name, ie.support_or_oppose(), candidate_fec_id, candidate_party, candidate_office, candidate_district, candidate_state, ie.expenditure_amount, ie.state, ie.expenditure_date, ie.election_type, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number ])
        
    return rows

def expenditure_csv(request, committee_id):
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id)
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(committee=committee).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Election Type', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = committee.slug + "_expenditures.csv"
    return generic_csv(expenditure_file_description, file_name, fields, rows) 

def all_expenditures_csv(request):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Election Type', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name =  "all_expenditures.csv"
            
    return generic_csv(expenditure_file_description, file_name, fields, rows)  
    
def all_expenditures_csv_to_file():
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Election Type', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    
    file_name =  "%s/all_expenditures.csv" % (CSV_EXPORT_DIR)

    write_csv_to_file(expenditure_file_description, file_name, fields, rows)
   

def expenditure_csv_state(request, state):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(state=state).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Election Type', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = state + "_expenditures.csv"
    return generic_csv(expenditure_file_description, file_name, fields, rows)    


def expenditure_csv_race(request, office, state, district):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(office=office).filter(superceded_by_amendment=False)
    if (office in ('H', 'S')):
        expenditures = expenditures.filter(candidate__state_race=state)
    if (office == 'H'):
        expenditures = expenditures.filter(candidate__district=district)    

    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Election Type','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Election Type', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = office + "_" + state + "_" + district + "_expenditures.csv"
    return generic_csv(expenditure_file_description, file_name, fields, rows)

def contribs_csv(request, committee_id):                            
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id)
    contributions = Contribution.objects.filter(fec_committeeid=committee_id, superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA14', 'SA15', 'SA16', 'SA17'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC','Transaction ID', 'Filing Number']
    rows = []
    file_name = committee.slug + "_donors.csv"

    for c in contributions:
        rows.append([c.contrib_source(), committee.name, committee_id, c.contrib_org, c.contrib_last, c.contrib_first, c.contrib_city, c.contrib_state, c.contrib_occupation, c.contrib_employer, c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number])
    return generic_csv(contribution_file_description, file_name, fields, rows)

def organizational_contribs_csv(request):

    contributions = Contribution.objects.select_related("committee", "candidate").filter(committee__isnull=False, superceded_by_amendment=False).exclude(contrib_org='').filter(line_type__in=['SA11AI', 'SA15'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'PAC political orientation','Donating organization', 'Donor street 1',  'Donor street 2', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC','Transaction ID', 'Filing Number', 'memo', 'memo text description']
    rows = []
    file_name = "organizational_donors.csv"

    for c in contributions:
        rows.append([c.contrib_source(), c.committee.name, c.committee.fec_id, c.committee.political_orientation, c.contrib_org, c.contrib_street_1, c.contrib_street_2, c.contrib_city, c.contrib_state, c.contrib_occupation, c.contrib_employer, c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number, c.memo_agg_item, c.memo_text_descript])
    return generic_csv(organizational_file_description, file_name, fields, rows)
    
    

def state_contribs_csv(request, state):                            
    contributions = Contribution.objects.filter(contrib_state=state.upper(), superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA14', 'SA15', 'SA16', 'SA17'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = state + "_donors.csv"

    for c in contributions:
        
        name = ''
        if (c.committee):
            name = c.committee.name
            
        rows.append([ c.contrib_source(), name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number])
    return generic_csv(contribution_file_description, file_name, fields, rows)        


def all_contribs_csv(request):                            
    contributions = Contribution.objects.filter(superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA14', 'SA15', 'SA16', 'SA17'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = "all_donors.csv"

    for c in contributions:
        name = ''
        if (c.committee):
            name = c.committee.name

        rows.append([ c.contrib_source(), name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number])
    return generic_csv(contribution_file_description, file_name, fields, rows)
    
def all_contribs_csv_to_file():                            
    contributions = Contribution.objects.filter(superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA14', 'SA15', 'SA16', 'SA17'])
    fields = ['Receipt Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Total amount given to this PAC', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = "all_donors.csv"

    for c in contributions:
        name = ''
        if (c.committee):
            name = c.committee.name

        rows.append([ c.contrib_source(), name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.contrib_agg, c.transaction_id, c.filing_number])
    
    file_name =  "%s/all_contribs.csv" % (CSV_EXPORT_DIR)

    write_csv_to_file(contribution_file_description, file_name, fields, rows)


def committee_summary_public(request):
    committees = Committee_Overlay.objects.filter( Q(is_superpac=True)|Q(total_indy_expenditures__gt=0) |Q(total_electioneering__gt=0)).select_related('committee_master_record')
    
    fields = ['Name', 'Committee ID', 'Is super pac', 'Party', 'Treasurer', 'Street_1', 'Street_2', 'City', 'ZIP code', 'state', 'connected_org_name', 'interest group category', 'committee type', 'designation', 'Filing frequency', 'Total contributions', 'Total unitemized contributions', 'cash on hand', 'last report date', 'total IEs', 'IEs support dems', 'IEs oppose dems', 'IEs support reps', 'IEs oppose reps', 'tax status']
    
    rows = []
    file_name = 'committee_summary.csv'
    
    
    for c in committees:
        
        interest_group_cat, ctype, designation, state = None, None, None, None
        if c.committee_master_record:
            interest_group_cat = c.committee_master_record.interest_group_cat
            ctype = c.display_type()
            designation = c.committee_master_record.designation
            state = c.committee_master_record.state_race

        rows.append([c.name, c.fec_id, c.superpac_status(), c.party, c.treasurer, c.street_1, c.street_2, c.city, c.zip_code, state, c.connected_org_name, interest_group_cat, ctype, designation, c.filing_frequency_text(), c.total_contributions, c.total_unitemized, c.cash_on_hand, c.cash_on_hand_date, c.total_indy_expenditures, c.ie_support_dems, c.ie_oppose_dems, c.ie_support_reps, c.ie_oppose_reps, c.org_status])
    return generic_csv("This is a summary of all groups that have made independent expenditures, are super PACs, or have made electioneering communications. Note that some groups may appear twice because they have multiple FEC identification numbers", file_name, fields, rows)
    
def superpac_political_orientation(request):
    committees = Committee_Overlay.objects.filter( Q(is_superpac=True)).select_related('committee_master_record')

    fields = ['Name', 'Committee ID', 'Treasurer', 'Street_1', 'Street_2', 'City', 'ZIP code', 'state', 'Connected Org Name', 'Political Orientation', 'Filing frequency', 'Total receipts (includes both itemized and unitemized contributions)', 'Total unitemized contributions', 'cash on hand', 'last report date', 'total IEs', 'IEs support dems', 'IEs oppose dems', 'IEs support reps', 'IEs oppose reps']

    rows = []
    file_name = 'committee_summary.csv'


    for c in committees:

        interest_group_cat, ctype, designation, state = None, None, None, None
        if c.committee_master_record:
            interest_group_cat = c.committee_master_record.interest_group_cat
            ctype = c.display_type()
            designation = c.committee_master_record.designation
            state = c.committee_master_record.state_race

        rows.append([c.name, c.fec_id, c.treasurer, c.street_1, c.street_2, c.city, c.zip_code, state, c.connected_org_name, c.display_political_orientation(), c.filing_frequency_text(), c.total_contributions, c.total_unitemized, c.cash_on_hand, c.cash_on_hand_date, c.total_indy_expenditures, c.ie_support_dems, c.ie_oppose_dems, c.ie_support_reps, c.ie_oppose_reps])
    return generic_csv("This file contains a listing of all super PACs and the political affiliation Sunlight has assigned to them", file_name, fields, rows)    

def committee_summary_private(request):
    committees = Committee_Overlay.objects.filter( Q(is_superpac=True)|Q(total_indy_expenditures__gt=0)|Q(total_electioneering__gt=0) ).select_related('committee_master_record')

    fields = ['Name', 'Committee ID', 'Is super pac', 'Party', 'Treasurer', 'Street_1', 'Street_2', 'City', 'ZIP code', 'state', 'connected_org_name', 'interest group category', 'committee type', 'designation', 'Filing frequency', 'Total contributions', 'Total unitemized contributions', 'cash on hand', 'last report date', 'total IEs', 'IEs support dems', 'IEs oppose dems', 'IEs support reps', 'IEs oppose reps', 'tax status', 'political_orientation', 'political orientation verified']

    rows = []
    file_name = 'committee_summary_details.csv'


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
def all_superpacs(request):
    explanatory_text = "This table shows all independent expenditure-only committees--better known as super PACs--that have raised or spent at least $10,000 since the beginning of 2011. The totals, listed above, are for all super PACs. Many groups that aren't super PACs are also making independent expenditures--for a more complete listing see the <a href=\"/outside-spending/all-outside-groups/\">biggest outside spending groups</a>. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site. For the much longer list of <a href='/outside-spending/super-pacs/complete-list/'>all superpacs</a> click <a href='/outside-spending/super-pacs/complete-list/'>here</a>."

    all_superpacs = Committee_Overlay.objects.filter(is_superpac=True)
    
    totals = all_superpacs.aggregate(support_dems=Sum('ie_support_dems'), oppose_dems=Sum('ie_oppose_dems'), oppose_reps=Sum('ie_oppose_reps'), support_reps=Sum('ie_support_reps'), total=Sum('total_indy_expenditures'), total_contribs=Sum('total_contributions'))
    
    total_amt = totals['total']
    neg_percent = 100*(totals['oppose_dems']+totals['oppose_reps'])/totals['total']
    positive_percent = 100*(totals['support_dems']+totals['support_reps'])/totals['total']
    
    
    
    superpacs = all_superpacs.filter(is_superpac=True).filter(Q(total_contributions__gte=10000)|Q(total_indy_expenditures__gte=10000))
    
    return render_to_response('outside_spending/superpac_list.html',
                            {'explanatory_text':explanatory_text, 
                            'superpacs':superpacs, 
                            'total_amt':total_amt, 
                            'total_contribs':totals['total_contribs'],
                            'neg_percent':neg_percent,
                            'pos_percent':positive_percent,
                            }) 

@cache_page(CACHE_TIME)                            
def all_independent_expenditors(request):
    explanatory_text = "This table shows all committees making independent expenditures that have spent at least $10,000 on independent expenditures since the beginning of 2011. The totals, listed above, are for all such groups, regardless of whether they are included below. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site."

    all_groups = Committee_Overlay.objects.filter()

    totals = all_groups.aggregate(support_dems=Sum('ie_support_dems'), oppose_dems=Sum('ie_oppose_dems'), oppose_reps=Sum('ie_oppose_reps'), support_reps=Sum('ie_support_reps'), total=Sum('total_indy_expenditures'), total_contribs=Sum('total_contributions'))
    


    total_amt = totals['total']
    neg_percent = 100*(totals['oppose_dems']+totals['oppose_reps'])/totals['total']
    positive_percent = 100*(totals['support_dems']+totals['support_reps'])/totals['total']

    all_groups = all_groups.filter(total_indy_expenditures__gte=10000)


    return render_to_response('outside_spending/all-outside-spenders.html',
                            {'explanatory_text':explanatory_text, 
                            'superpacs':all_groups, 
                            'total_amt':total_amt, 
                            'total_contribs':totals['total_contribs'],
                            'neg_percent':neg_percent,
                            'pos_percent':positive_percent,
                            })

def all_electioneering_groups(request):
    explanatory_text = "This table shows all committees that have spent at least $1,000 on electioneering communications since the beginning of 2011. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site. The Federal Election Commission creates separate committees for electioneering communications, so many of these groups have affiliated groups devoted to other types of political spending; try searching for a committee name to find it.<br>Also see a <a href='/outside-spending/electioneering-communications/'>list of the most recent electioneering communications</a>."

    all_groups = Committee_Overlay.objects.filter(total_electioneering__gt=1000)


    return render_to_response('outside_spending/all_electioneers.html',
                            {'explanatory_text':explanatory_text, 
                            'superpacs':all_groups, 
                            })
    
    
                            
@cache_page(CACHE_TIME)                            
def october_club(request):
    explanatory_text = "This table shows committees that began making expenditures in October or November of 2012 and have spent at least $50,000 to date." 
    october_first = datetime.date(2012,10,1)
    summaries = Expenditure.objects.filter(superceded_by_amendment=False, expenditure_date__gte=october_first,committee__total_indy_expenditures__gte=50000).select_related("committee").values('committee__fec_id', 'committee__name', 'committee__slug', 'committee__total_indy_expenditures', 'committee__ctype', 'committee__cash_on_hand_date').annotate(postseptember=Sum('expenditure_amount')).annotate(firstbuy=Min('expenditure_date'))
    october_club = []
    for summary in summaries:
        if summary['postseptember'] == summary['committee__total_indy_expenditures']:
            october_club.append(summary)
    



    return render_to_response('outside_spending/october_club.html',
                            {'explanatory_text':explanatory_text, 
                            'superpacs':october_club, 
                            })

@cache_page(CACHE_TIME)
def complete_superpac_list(request):
    superpacs = Committee_Overlay.objects.filter(is_superpac=True).order_by('total_indy_expenditures')
    explanatory_text= 'This is a list of all super PACs.'
    return render_to_response('outside_spending/superpac_show_all.html',
                            {'superpacs':superpacs,
                            'explanatory_text':explanatory_text,
                            })  

@cache_page(CACHE_TIME)                            
def committee_detail(request,committee_id):
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id)
    expenditures = Expenditure.objects.filter(committee=committee).filter(superceded_by_amendment=False).select_related('committee', 'candidate')
    contributions = Contribution.objects.filter(fec_committeeid=committee_id, superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA15'])
    candidates_supported = Pac_Candidate.objects.filter(committee=committee)
    explanatory_text = 'This table shows the overall total amount spent by this group supporting or opposing federal candidates in independent expenditures in the 2012 election cycle.'
    explanatory_text_details = 'This table shows the independent expenditures of $10,000 or more made by this group supporting or opposing federal candidates in the 2012 election cycle. To view a more detailed file of all such spending, <a href=\"%s\">click here</a>.' % (committee.superpachackcsv())
    explanatory_text_contribs = 'This table shows all contributions, related PAC transfers and operating expense offsets made to this group during the 2012 campaign cycle, as of %s. Operating expense offsets are marked with an asterisk (*). To view a more detailed file of this spending, which includes all receipt types, <a href=\"%s\">click here</a>.' % (committee.cash_on_hand_date,committee.superpachackdonorscsv())

    ecs = Electioneering_93.objects.select_related("target", "target__candidate").filter(superceded_by_amendment=False, fec_id=committee_id).order_by('-exp_date')
    ec_total_dict = ecs.aggregate(total=Sum('exp_amo'))
    ec_total = ec_total_dict['total']

    # ie monthly summary

    monthly_ie_data = Expenditure.objects.filter(committee=committee).filter(superceded_by_amendment=False).extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()
    show_current_month = True

    monthly_ie_summary = summarize_monthly(monthly_ie_data, today, show_current_month)
    
    display_expenditures = expenditures.filter(expenditure_amount__gte=10000)

    monthly_contrib_summary = None
    if (committee.is_superpac):
        monthly_contrib_data = Contribution.objects.filter(fec_committeeid=committee_id, superceded_by_amendment=False, line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA15']).extra(select={'year': 'EXTRACT(year FROM contrib_date)','month': 'EXTRACT(month FROM contrib_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('contrib_amt'))
        monthly_contrib_summary = summarize_monthly(monthly_contrib_data, committee.cash_on_hand_date, True)
        
    has_chart = False 
    print "length is %s" % (len(monthly_ie_data))    
    if (committee.is_superpac or len(monthly_ie_data) > 0):
        has_chart = True

    return render_to_response('outside_spending/committee_detail_2.html',
                            {'committee':committee, 
                            'expenditures':display_expenditures,
                            'contributions':contributions, 
                            'candidates':candidates_supported,
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details,
                            'explanatory_text_contribs':explanatory_text_contribs,
                            'ecs':ecs,
                            'ec_explanation':electioneering_details,
                            'ec_total':ec_total, 
                            'monthly_ie_summary':monthly_ie_summary,
                            'monthly_contrib_summary':monthly_contrib_summary,
                            'has_chart':has_chart
                            })                            

def presidential_superpacs(request):
    explanatory_text = "This table shows all independent expenditure-only committees--better known as super PACs--that have spent more than $1,000 in independent expenditures in support of a presidential candidate during the 2012 primrary election cycle. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site."

    superpacs = Committee_Overlay.objects.filter(total_presidential_indy_expenditures__gte=1000)
    total = superpacs.aggregate(total=Sum('total_presidential_indy_expenditures'))
    total_amt = total['total']   
     

    return render_to_response('outside_spending/presidential_superpac_list.html',
                            {'explanatory_text':explanatory_text, 
                            'superpacs':superpacs,
                            'total_amt':total_amt})

def presidential_state_summary(request, state):
    try:
        state_name = STATE_CHOICES[state]
    except KeyError:
        raise Http404

    state_pacs = President_State_Pac_Aggregate.objects.filter(state=state)

    expenditures = Expenditure.objects.filter(superceded_by_amendment=False, state=state, office='P').select_related("committee", "candidate")
    explanatory_text = 'This is a list of groups that have made independent expenditures for or against a presidential candidate during the primary election in the state of ' + state_name + '. The FEC does not require political groups to say what state they spent their money in during the general election.'
    explanatory_text_details = 'This is a list all independent expenditures made for or against a presidential candidate during the primary election in the state of ' + state_name + '. The FEC does not require political groups to say what state they spent their money in during the general election.'
    
    ecs = Electioneering_93.objects.select_related("target", "target__candidate").filter(superceded_by_amendment=False, target__candidate__office='P', target__can_state=state).order_by('-exp_date')
    
    

    return render_to_response('outside_spending/state_presidential_detail.html',
                            {'state_pacs':state_pacs, 
                            'state_name':state_name,
                            'explanatory_text':explanatory_text,
                            'expenditures':expenditures,
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details,
                            'ecs':ecs,
                            'ec_explanation':electioneering_details
                            })

@cache_page(CACHE_TIME)
def races(request):
    races = Race_Aggregate.objects.exclude(district__isnull=True)
    explanatory_text = "This page shows independent expenditures made in the 2012 election cycle by race. Click on each race to see aggregate totals by candidate, and to get access to a downloadable file of all individual expenditures for this race. " + electioneering_details
    return render_to_response('outside_spending/race_list.html',
                            {'races':races, 
                            'explanatory_text':explanatory_text
                            })
                            
def race_detail(request, office, state, district):
    race_aggregate = get_object_or_404(Race_Aggregate, office=office, state=state, district=district)
    candidate_pacs = Pac_Candidate.objects.filter(candidate__office=office, candidate__state_race=state, candidate__district=district)
    ecs = Electioneering_93.objects.select_related("target", "target__candidate").filter(superceded_by_amendment=False, target__candidate__office=office, target__candidate__state_race=state, target__candidate__district=district).order_by('-exp_date')
    
    explanatory_text = "This table shows the total amount of independent expenditures each group made to support or oppose a candidate in this race. For a downloadable file of this information, <a href=\"/outside-spending/csv/race/expenditures/%s/%s/%s/\">click here</a>." % (office, state, district)
    race_name = None
    if (office=='P'):
        race_name = 'President'
    elif office == 'S':
        race_name = '%s (Senate)' % state
    else:
        race_name='%s-%s (House)' % (state, district.lstrip('0'))

    return render_to_response('outside_spending/race_detail.html',
                            {'candidates':candidate_pacs, 
                            'explanatory_text':explanatory_text, 
                            'race_name':race_name,
                            'race_aggregate':race_aggregate, 
                            'ecs':ecs,
                            'ec_explanation':electioneering_details
                            })      
@cache_page(CACHE_TIME)                            
def candidates(request):
    candidates = Candidate_Overlay.objects.filter(total_expenditures__gte=10)
    explanatory_text= 'This table lists all independent expenditures made to support or oppose federal candidates during the 2012 election cycle, and all electioneering communications. Candidates not targeted by either type of spending are not included. ' + electioneering_details
    return render_to_response('outside_spending/candidate_list.html',
                            {'candidates':candidates, 
                            'explanatory_text':explanatory_text,
                            }) 
                            
def candidate_detail(request, candidate_id):
    candidate = Candidate_Overlay.objects.get(fec_id=candidate_id)
    explanatory_text= 'This is a list of all super PACs that have made independent expenditures supporting or opposing this candidate.'
    explanatory_text_details = 'This is a list of all independent expenditures of $10,000 or more made by any committee for or against this candidate.'
    superpacs = Pac_Candidate.objects.filter(candidate=candidate)
    expenditures = Expenditure.objects.filter(superceded_by_amendment=False, candidate=candidate, expenditure_amount__gte=10000).select_related("committee")
    
    ecs = Electioneering_93.objects.select_related("target", "target__candidate").filter(superceded_by_amendment=False, target__candidate=candidate).order_by('-exp_date')
    ec_total_dict = ecs.aggregate(total=Sum('exp_amo'))
    ec_total = ec_total_dict['total']
    
    return render_to_response('outside_spending/candidate_detail.html',
                            {'candidate':candidate, 
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details,
                            'superpacs':superpacs,
                            'expenditures':expenditures,
                            'ecs':ecs,
                            'ec_explanation':electioneering_details,
                            'ec_total':ec_total,
                            }) 

def states(request):
    states = State_Aggregate.objects.filter(total_ind_exp__gt=0)
    explanatory_text= 'This table lists the sums of independent expenditures and electioneering communications reported to have been made in each state during the 2012 election cycle. The FEC does not require that general election spending in support of a president be designated to a particular state. Moreover, the state designation is sometimes omitted from reports where it should be included. Therefore, the totals on this page will not match overall totals found elsewhere on this site. For downloadable state-by-state files, see the <a href="/outside-spending/file-downloads/">downloads page</a>. ' + electioneering_details
    return render_to_response('outside_spending/state_list.html',
                            {'states':states, 
                            'explanatory_text':explanatory_text,
                            })                                                                                                        

def state_detail(request, state_abbreviation):

    try:
        state_name = STATE_CHOICES[state_abbreviation]
    except KeyError:
        raise Http404


    races = Race_Aggregate.objects.filter(state__iexact=state_abbreviation).exclude(district__isnull=True)
    this_state = State_Aggregate.objects.get(state=state_abbreviation)

    candidates = Candidate_Overlay.objects.filter(total_expenditures__gte=10, state_race__iexact=state_abbreviation)

    explanatory_text= 'For a downloadable .csv file of this information, <a href="/outside-spending/csv/state/expenditures/%s/">click here</a>.</p><p>This table lists the total of all independent expenditures and electioneering communications designated to this state during the 2012 election cycle by race. The FEC does not require that general election spending in support of a president be designated to a particular state. Moreover, the state designation is sometimes omitted from reports where it should be included.' % (state_abbreviation)
    return render_to_response('outside_spending/state_detail.html',
                            {'races':races, 
                            'state_name':state_name,
                            'candidates':candidates,
                            'explanatory_text':explanatory_text,
                            'this_state':this_state
                            })

@cache_page(CACHE_TIME)
def ies(request):
    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=7)
    ies = Expenditure.objects.select_related("committee", "candidate").filter(superceded_by_amendment=False, expenditure_date__gte=two_weeks_ago, expenditure_amount__gte=50000).order_by('-expenditure_date')
    explanatory_text= 'This page shows independent expenditures made in the last 7 days for $50,000 or more. See the <a href="http://assets.sunlightfoundation.com/reporting/FTUM-data/all_expenditures.csv">complete file</a> of independent expenditures for amounts less than $50,000.'
    return render_to_response('outside_spending/expenditure_list.html',
                            {'ies':ies, 
                            'explanatory_text':explanatory_text,
                            })


def ecs(request):
    #today = datetime.date.today()
    #two_weeks_ago = today - datetime.timedelta(days=14)
    ecs = Electioneering_93.objects.select_related("target", "target__candidate").filter(superceded_by_amendment=False, exp_amo__gte=50000).order_by('-exp_date')
    #explanatory_text= 'This page shows electioneering communications.'
    return render_to_response('outside_spending/electioneering_list.html',
                            {'ecs':ecs, 
                            'explanatory_text':electioneering_details + "<br>This list includes amounts of $50,000 or more. Also see <a href='/outside-spending/electioneering-groups/'>a summary of electioneering groups</a>"
                            })


@cache_page(CACHE_TIME)
def organizational_superpac_contribs(request):
    contribs = Contribution.objects.select_related("committee").filter(committee__isnull=False, superceded_by_amendment=False).exclude(contrib_org='').filter(line_type__in=['SA11AI', 'SA15'])


    total = contribs.aggregate(total=Sum('contrib_amt'))
    total_amt = total['total']

    explanatory_text= 'This is a list of all contributions to super PACs from organizations, including money received as operating expense offsets. These offsets, which are marked with an asterisk below, often include administrative overhead paid by a related organization, though sometimes include refund payments. This list does not include contributions from corporate--or any other--PACs. Also see a <a href="/outside-spending/noncommittees/">summary page of non-committees making independent expenditures</a>.'
    return render_to_response('outside_spending/organizational_contribs.html',
                            {'contribs':contribs,
                            'total_amt':total_amt,
                            'explanatory_text':explanatory_text,
                            })
@cache_page(CACHE_TIME)                            
def file_downloads(request):
    committees = Committee_Overlay.objects.filter(total_contributions__gte=1000).order_by('name')
    states = State_Aggregate.objects.filter(total_ind_exp__gt=0).order_by('state')
    races = Race_Aggregate.objects.filter(total_ind_exp__gt=0).order_by('state', 'office', 'district')

    return render_to_response('outside_spending/file_downloads.html',
                            {'committees':committees, 
                            'states':states,
                            'races':races,
                            })  



@cache_page(60 * 60)                              
def overview(request):
    ## should put these aggregates in a table, but... 
    
    all_ies = Committee_Overlay.objects.all()
    #total_ie = all_ies.aggregate(total=Sum('total_indy_expenditures'))
    #total_ies = total_ie['total']
    
    all_superpacs = all_ies.filter(is_superpac=True)
    total_sp = all_superpacs.aggregate(total=Sum('total_indy_expenditures'))
    total_sp_ies = total_sp['total']
    total_sps = len(all_superpacs)
    
    ecs = Electioneering_93.objects.filter(superceded_by_amendment=False)
    total_ecs = ecs.aggregate(total=Sum('exp_amo'))['total']

    
    contribs = Contribution.objects.filter(line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA15'], superceded_by_amendment=False)
    total_contribs_amt = contribs.aggregate(total=Sum('contrib_amt'))
    total_contribs = total_contribs_amt['total']
    
    list_all_ies = Expenditure.objects.filter(superceded_by_amendment=False, committee__isnull=False).select_related("candidate")
    total_ies = list_all_ies.aggregate(total=Sum('expenditure_amount'))['total']
    pres_ies = list_all_ies.filter(candidate__office='P').aggregate(total=Sum('expenditure_amount'))['total']
    house_ies = list_all_ies.filter(candidate__office='H').aggregate(total=Sum('expenditure_amount'))['total']
    senate_ies = list_all_ies.filter(candidate__office='S').aggregate(total=Sum('expenditure_amount'))['total']
    supporting_ies = list_all_ies.filter(support_oppose='S').aggregate(total=Sum('expenditure_amount'))['total']
    opposing_ies = list_all_ies.filter(support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total']
    
    noncommittee_ies = list_all_ies.filter(committee__ctype='I').aggregate(total=Sum('expenditure_amount'))['total']
    nonparty_ies = list_all_ies.filter(committee__ctype__in=('N', 'Q')).aggregate(total=Sum('expenditure_amount'))['total']
    party_ies = list_all_ies.filter(committee__ctype__in=('Y', 'Z')).aggregate(total=Sum('expenditure_amount'))['total']
    
    # for chart
    #superpac_ies = list_all_ies.filter(committee__is_superpac=True)
    
    
    
    
    contribs = Contribution.objects.select_related("committee").filter(committee__isnull=False).exclude(contrib_org='').filter(superceded_by_amendment=False, line_type__in=['SA11AI', 'SA15'])
    total_organizational = contribs.aggregate(total=Sum('contrib_amt'))['total']

    
    
    
    return render_to_response('outside_spending/overview.html',
        {'total_ies':total_ies,
        'total_sp_ies':total_sp_ies,
        'total_contribs':total_contribs,
        'total_sps':total_sps,
        'total_ecs':total_ecs,
        'pres_ies':pres_ies, 
        'senate_ies':senate_ies,
        'house_ies':house_ies,
        'supporting_ies':supporting_ies,
        'opposing_ies':opposing_ies,
        'total_organizational':total_organizational, 
        'noncommittee_ies': noncommittee_ies,
        'nonparty_ies':nonparty_ies,
        'party_ies':party_ies,
        'div_name_1':'superpac_chart',
        'div_name_2':'noncommittees', 
        'div_name_3':'nonparty', 
        'div_name_4':'party', 
        'div_name_0':'all_ies'
        })
        


def recent_fec_filings(request):
    
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    filings = unprocessed_filing.objects.all().order_by('-filing_number')[:50]
    title="Recent FEC Filings"
    explanatory_text="All recent electronic FEC filings. Filings made on paper are not included."
    
    return render_to_response('outside_spending/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )    
    
def recent_ie_filings(request):

    filings = unprocessed_filing.objects.filter(form_type__in=['F5A', 'F5N', 'F24A', 'F24N']).order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Recent Independent Expenditure Filings"
    explanatory_text="These are recent electronic FEC filings that show independent expenditures--specifically, forms F24 and F5."

    return render_to_response('outside_spending/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )    
    
def significant_committees(request):

    filings = unprocessed_filing.objects.filter(fec_id__in=['C00431171', 'C00496497', 'C00496034', 'C00495820', 'C00010603', 'C00042366', 'C00000935', 'C00003418', 'C00027466', 'C00075820', 'C00431445']).order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Notable PAC Filings"
    explanatory_text="These are recent electronic FEC filings from major presidential candidates and party committees."

    return render_to_response('outside_spending/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )
    
def significant_committees_new(request):

    filings = unprocessed_filing.objects.filter(fec_id__in=['C00431171', 'C00496497', 'C00496034', 'C00495820', 'C00010603', 'C00042366', 'C00000935', 'C00003418', 'C00027466', 'C00075820', 'C00431445'], form_type__in=['F3XN', 'F3N', 'F3PN']).order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Monthly / Quarterly Filings From Major PACs"
    explanatory_text="These are recent monthly / quarterly electronic FEC filings from major presidential candidates and party committees. Amended filings are not included. "

    return render_to_response('outside_spending/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )    
def recent_superpac_filings(request): 
    
    filings = unprocessed_filing.objects.filter(is_superpac=True).order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='Super PAC Filings'
    explanatory_text="These are recent electronic FEC filings from super PACs."

    return render_to_response('outside_spending/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )   
    
def recent_superpac_filings_f3x(request): 

    filings = unprocessed_filing.objects.filter(is_superpac=True, form_type='F3XN').order_by('-filing_number')[:50]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='Original Monthly / Quarterly Super PAC Filings'
    explanatory_text="These are new monthly / quarterly reports from super PACs (ie form F3XN). Amended filings are not included. "

    return render_to_response('outside_spending/recent_fec_filings.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )    
    
def recent_fec_filings_mobile(request):

    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    filings = unprocessed_filing.objects.all().order_by('-filing_number')[:25]
    title="Recent FEC Filings  - FEC filings - Sunlight Foundation"
    explanatory_text="All recent electronic FEC filings. Filings made on paper are not included."

    return render_to_response('mobile_test/fec_alerts_index.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )
    
def recent_fec_filings_ies(request):

    filings = unprocessed_filing.objects.filter(form_type__in=['F5A', 'F5N', 'F24A', 'F24N']).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Recent Independent Expenditures - FEC filings - Sunlight Foundation"
    explanatory_text="These are recent electronic FEC filings that show independent expenditures--specifically, forms F24 and F5."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )    

def recent_fec_filings_significant(request):

    filings = unprocessed_filing.objects.filter(fec_id__in=['C00431171', 'C00496497', 'C00496034', 'C00495820', 'C00010603', 'C00042366', 'C00000935', 'C00003418', 'C00027466', 'C00075820', 'C00431445']).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Notable PACs  - FEC filings - Sunlight Foundation"
    explanatory_text="These are recent electronic FEC filings from major presidential candidates and party committees."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_significant_new(request):

    filings = unprocessed_filing.objects.filter(fec_id__in=['C00431171', 'C00496497', 'C00496034', 'C00495820', 'C00010603', 'C00042366', 'C00000935', 'C00003418', 'C00027466', 'C00075820', 'C00431445'], form_type__in=['F3XN', 'F3N', 'F3PN']).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title="Notable PACs  - FEC filings - Sunlight Foundation"
    explanatory_text="These are recent electronic monthly / quarterly filings from major presidential candidates and party committees."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_superpacs(request): 

    filings = unprocessed_filing.objects.filter(is_superpac=True).order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='Super PAC Filings - FEC filings - Sunlight Foundation'
    explanatory_text="These are recent electronic FEC filings from super PACs."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_superpacs_f3x(request): 

    filings = unprocessed_filing.objects.filter(is_superpac=True, form_type="F3XN").order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='Super PAC Filings - FEC filings - Sunlight Foundation'
    explanatory_text="These are recent electronic monthly / quarterly reports from super PACs."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

def recent_fec_filings_48hr_contrib(request):
    filings = unprocessed_filing.objects.filter(form_type='F6N').order_by('-filing_number')[:25]
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    title='48-hr Contribution Reports - FEC filings - Sunlight Foundation'
    explanatory_text="These 48 hour reports are used to disclose the receipt of last-minute contributions of $1,000 or more. Principal campaign committees must file these notices for contributions received after the 20th day, but more than 48 hours, before the day the candidate's election."

    return render_to_response('mobile_test/fec_alerts_more.html',
        {
        'title':title,
        'explanatory_text':explanatory_text,
        'filings':filings,
        'update_time':update_time
        }
    )

    
    
def committee_search_json(request): 
    params = request.GET
    committees = None
    
    try:
        committee_name_fragment =  params['name']
        if len(committee_name_fragment) > 3:
            print committee_name_fragment
            
            
            committees = Committee.objects.filter(Q(name__icontains=committee_name_fragment) | Q(related_candidate__fec_name__icontains=committee_name_fragment)).select_related()
        else:
            committees = None
    except KeyError:
        committees = None

    return render_to_response('mobile_test/committee_search.json',
        {
        'committees':committees,
        }
    ) 
    
    
def committee_search_html(request): 
    params = request.GET
    committees = None

    try:
        committee_name_fragment =  params['name']
        if len(committee_name_fragment) > 3:
            print committee_name_fragment


            committees = Committee.objects.filter(Q(name__icontains=committee_name_fragment) | Q(related_candidate__fec_name__icontains=committee_name_fragment)).select_related()
        else:
            committees = None
    except KeyError:
        committees = None

    return render_to_response('mobile_test/committee_search_2.html',
        {
        'committees':committees,
        }
    )    
def subscribe_to_alerts(request):
    
    return render_to_response('outside_spending/subscribe.html',
        {}
    )

def noncommittees(request):
    noncommittees = Committee_Overlay.objects.filter(committee_master_record__ctype='I')
    totals = noncommittees.aggregate(support_dems=Sum('ie_support_dems'), oppose_dems=Sum('ie_oppose_dems'), oppose_reps=Sum('ie_oppose_reps'), support_reps=Sum('ie_support_reps'), total=Sum('total_indy_expenditures'))
    neg_percent = 100*(totals['oppose_dems']+totals['oppose_reps'])/totals['total']
    positive_percent = 100*(totals['support_dems']+totals['support_reps'])/totals['total']
    explanatory_text = """The following groups and individuals are not registered with the Federal Election Commission as political committees because they say their major purpose is not political. The totals shown below are only for the fraction of their spending deemed 'independent expenditures'; many of these groups have also spent tens of millions of dollars trying to influence the election through 'issue ads' run months before the election, when they aren't required to be disclosed. These groups only have to report their donors if money was given for a specific independent expenditure."""
    
    return render_to_response('outside_spending/noncommittees.html',
        {
        'explanatory_text':explanatory_text,
        'noncommittees':noncommittees,
        'totals':totals,
        'neg_percent':neg_percent,
        'pos_percent':positive_percent,
        }
    )
# API-ish stuff

def candidate_summary_json(request, candidate_id):
    candidate = Candidate_Overlay.objects.get(fec_id=candidate_id)
    superpacs = Pac_Candidate.objects.filter(candidate=candidate).select_related()
    
    return render_to_json('outside_spending/candidate_summary.json', {
                'candidate':candidate, 
                'superpacs':superpacs,
                })


def search(request):
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

    
    return render_to_response('outside_spending/search.html', {
                'terms':terms,
                'invalid_search':invalid_search, 
                'num_results':num_results,
                'committee_overlays':committee_overlays,
                'committees':committees,
                'has_committees':has_committees,
                'candidate_overlays':candidate_overlays,
                'has_candidates':has_candidates,
                'candidates':candidates,
                })
                
                
def more_resources(request):
    return render_to_response('outside_spending/more_resources.html', {
    
    })
    
 
# for feeding data to ad hawk
def committee_summary_json(request):
    committees = Committee_Overlay.objects.filter( Q(total_indy_expenditures__gt=0) |Q(total_electioneering__gt=0)).select_related('committee_master_record')

    return render_to_json('outside_spending/committee_summary.json', {
                'committees':committees
                })
                
@cache_page(60 * 30)
def by_affiliation(request):
    # for cash on hand:
    sps = Committee_Overlay.objects.filter(is_superpac=True)
    dem_coh = sps.filter(political_orientation='D').aggregate(total=Sum('cash_on_hand'))['total']
    rep_coh = sps.filter(political_orientation='R').aggregate(total=Sum('cash_on_hand'))['total']    
    oth_coh = sps.exclude(political_orientation__in=('D','R')).aggregate(total=Sum('cash_on_hand'))['total']
    
    all_contribs = Contribution.objects.filter(superceded_by_amendment=False).select_related('committee')
    dem_contribs = all_contribs.filter(committee__political_orientation='D').aggregate(total=Sum('contrib_amt'))['total']
    rep_contribs = all_contribs.filter(committee__political_orientation='R').aggregate(total=Sum('contrib_amt'))['total']
    oth_contribs = all_contribs.exclude(committee__political_orientation__in=('D', 'R')).aggregate(total=Sum('contrib_amt'))['total']    
    
    all_sp_ies = Expenditure.objects.filter(superceded_by_amendment=False, committee__is_superpac=True).select_related('committee')
    dem_sp_ies = all_sp_ies.filter(committee__political_orientation='D').aggregate(total=Sum('expenditure_amount'))['total']
    rep_sp_ies = all_sp_ies.filter(committee__political_orientation='R').aggregate(total=Sum('expenditure_amount'))['total']
    oth_sp_ies =  all_sp_ies.exclude(committee__political_orientation__in=('D', 'R')).aggregate(total=Sum('expenditure_amount'))['total']
    
    general_sp_ies = Expenditure.objects.filter(superceded_by_amendment=False, committee__is_superpac=True, election_type='G').select_related('committee')
    dem_general_sp_ies = general_sp_ies.filter(committee__political_orientation='D').aggregate(total=Sum('expenditure_amount'))['total']
    rep_general_sp_ies = general_sp_ies.filter(committee__political_orientation='R').aggregate(total=Sum('expenditure_amount'))['total']
    oth_general_sp_ies =  general_sp_ies.exclude(committee__political_orientation__in=('D', 'R')).aggregate(total=Sum('expenditure_amount'))['total']
    
    general_nc_ies = Expenditure.objects.filter(superceded_by_amendment=False, committee__ctype='I', election_type='G').select_related('committee')
    dem_general_nc_ies = general_nc_ies.filter(committee__political_orientation='D').aggregate(total=Sum('expenditure_amount'))['total']
    rep_general_nc_ies = general_nc_ies.filter(committee__political_orientation='R').aggregate(total=Sum('expenditure_amount'))['total']
    oth_general_nc_ies =  general_nc_ies.exclude(committee__political_orientation__in=('D', 'R')).aggregate(total=Sum('expenditure_amount'))['total']
    
    general_party_ies = Expenditure.objects.filter(superceded_by_amendment=False, committee__ctype__in=('Y', 'Z'), election_type='G').select_related('committee')
    dem_general_party_ies = general_party_ies.filter(committee__political_orientation='D').aggregate(total=Sum('expenditure_amount'))['total']
    rep_general_party_ies = general_party_ies.filter(committee__political_orientation='R').aggregate(total=Sum('expenditure_amount'))['total']
    oth_general_party_ies =  general_party_ies.exclude(committee__political_orientation__in=('D', 'R')).aggregate(total=Sum('expenditure_amount'))['total']
    
    return render_to_response('outside_spending/superpac_party_breakdown.html', 
    {
    'dem_coh':dem_coh,
    'rep_coh':rep_coh,
    'oth_coh':oth_coh,
    
    'dem_contribs':dem_contribs,
    'rep_contribs':rep_contribs,
    'oth_contribs':oth_contribs,
    
    'dem_sp_ies':dem_sp_ies,
    'rep_sp_ies':rep_sp_ies,
    'oth_sp_ies':oth_sp_ies,

    'dem_general_sp_ies':dem_general_sp_ies,
    'rep_general_sp_ies':rep_general_sp_ies,
    'oth_general_sp_ies':oth_general_sp_ies,

    'dem_general_nc_ies':dem_general_nc_ies,
    'rep_general_nc_ies':rep_general_nc_ies,
    'oth_general_nc_ies':oth_general_nc_ies,

    'dem_general_party_ies':dem_general_party_ies,
    'rep_general_party_ies':rep_general_party_ies,
    'oth_general_party_ies':oth_general_party_ies,

    'div_name_5':'superpac_by_party', 
    'div_name_6':'contribs_by_party', 
    'div_name_8':'partisan_general',
    'div_name_9':'noncommittee_partisan_general',
    'div_name_10':'party_committee_general',
    
    })
    
@cache_page(60*30)
def by_spending(request):
    
    all_pres_general_ies = Expenditure.objects.filter(superceded_by_amendment=False,candidate__office='P', election_type="G").select_related('candidate')
    dem_general_pres_ies = all_pres_general_ies.filter(Q(candidate__party__iexact='DEM', support_oppose='S')|Q(candidate__party__iexact='REP', support_oppose='O')).aggregate(total=Sum('expenditure_amount'))['total']
    rep_general_pres_ies = all_pres_general_ies.filter(Q(candidate__party__iexact='REP', support_oppose='S')|Q(candidate__party__iexact='DEM', support_oppose='O')).aggregate(total=Sum('expenditure_amount'))['total']
    
    
    all_sen_general_ies = Expenditure.objects.filter(superceded_by_amendment=False,candidate__office='S', election_type="G").select_related('candidate')
    dem_general_sen_ies = all_sen_general_ies.filter(Q(candidate__party__iexact='DEM', support_oppose='S')|Q(candidate__party__iexact='REP', support_oppose='O')).aggregate(total=Sum('expenditure_amount'))['total']
    rep_general_sen_ies = all_sen_general_ies.filter(Q(candidate__party__iexact='REP', support_oppose='S')|Q(candidate__party__iexact='DEM', support_oppose='O')).aggregate(total=Sum('expenditure_amount'))['total']
    
    all_house_general_ies = Expenditure.objects.filter(superceded_by_amendment=False,candidate__office='H', election_type="G").select_related('candidate')
    dem_general_house_ies = all_house_general_ies.filter(Q(candidate__party__iexact='DEM', support_oppose='S')|Q(candidate__party__iexact='REP', support_oppose='O')).aggregate(total=Sum('expenditure_amount'))['total']
    rep_general_house_ies = all_house_general_ies.filter(Q(candidate__party__iexact='REP', support_oppose='S')|Q(candidate__party__iexact='DEM', support_oppose='O')).aggregate(total=Sum('expenditure_amount'))['total']
    
    return render_to_response('outside_spending/by_spending.html', 
    {
    'dem_general_pres_ies':dem_general_pres_ies,
    'rep_general_pres_ies':rep_general_pres_ies,
    'dem_general_sen_ies':dem_general_sen_ies,
    'rep_general_sen_ies':rep_general_sen_ies,
    'dem_general_house_ies':dem_general_house_ies,
    'rep_general_house_ies':rep_general_house_ies,
    'div_name_1':'pres_gen_ies', 
    'div_name_2':'pres_sen_ies',
    'div_name_3':'pres_house_ies',        
    })

@cache_page(60 * 10)
def chart_embed(request):
    return render_to_response('outside_spending/chart_embedder.html', 
    {'div_name':'this_is_the_chart_div'})
    

@cache_page(60 * 30)
def elex_json(request):
    
    all_ies = Committee_Overlay.objects.all()
    #total_ie = all_ies.aggregate(total=Sum('total_indy_expenditures'))
    #total_ies = total_ie['total']
    
    all_superpacs = all_ies.filter(is_superpac=True)
    total_sp = all_superpacs.aggregate(total=Sum('total_indy_expenditures'))
    total_sp_ies = total_sp['total']

    
    ecs = Electioneering_93.objects.filter(superceded_by_amendment=False)
    total_ecs = ecs.aggregate(total=Sum('exp_amo'))['total']
    
    contribs = Contribution.objects.filter(line_type__in=['SA11AI', 'SA11B', 'SA11C', 'SA12', 'SA15'], superceded_by_amendment=False)
    total_contribs_amt = contribs.aggregate(total=Sum('contrib_amt'))
    total_contribs = total_contribs_amt['total']
    
    list_all_ies = Expenditure.objects.filter(superceded_by_amendment=False, committee__isnull=False).select_related("candidate")
    total_ies = list_all_ies.aggregate(total=Sum('expenditure_amount'))['total']
    pres_ies = list_all_ies.filter(candidate__office='P').aggregate(total=Sum('expenditure_amount'))['total']
#    house_ies = list_all_ies.filter(candidate__office='H').aggregate(total=Sum('expenditure_amount'))['total']
#    senate_ies = list_all_ies.filter(candidate__office='S').aggregate(total=Sum('expenditure_amount'))['total']
#    supporting_ies = list_all_ies.filter(support_oppose='S').aggregate(total=Sum('expenditure_amount'))['total']
#    opposing_ies = list_all_ies.filter(support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total']
    
    noncommittee_ies = list_all_ies.filter(committee__ctype='I').aggregate(total=Sum('expenditure_amount'))['total']
    nonparty_ies = list_all_ies.filter(committee__ctype__in=('N', 'Q')).aggregate(total=Sum('expenditure_amount'))['total']
    party_ies = list_all_ies.filter(committee__ctype__in=('Y', 'Z')).aggregate(total=Sum('expenditure_amount'))['total']
    
    total_outside = total_ies + total_ecs
    
    top_groups = Committee_Overlay.objects.all().order_by('-total_indy_expenditures')[:5]
    
    top_house_races = Race_Aggregate.objects.filter(office='H').order_by('-total_ind_exp')[:5]
    top_senate_races = Race_Aggregate.objects.filter(office='S').order_by('-total_ind_exp')[:5]
    
    return render_to_json('outside_spending/election_summary.json', {
                'total_outside':total_outside,
                'pres_ies':pres_ies,
                'superpac_contribs':total_contribs,
                'superpac_ies':total_sp_ies,
                'noncommittee_ies':noncommittee_ies,
                'nonparty_ies':nonparty_ies,
                'party_ies':party_ies,
                'top_outside_groups':top_groups,
                'update_time':most_recent_scrape, 
                'top_house_races':top_house_races,
                'top_senate_races':top_senate_races,
                })