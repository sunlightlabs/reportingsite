# Create your views here.
import csv
import datetime

from django.views.decorators.cache import cache_page
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response, redirect
from django.http import Http404, HttpResponse
from django.db.models import Sum
from django.db.models import Q
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.humanize.templatetags.humanize import intcomma

STATE_CHOICES = dict(STATE_CHOICES)

from rebuckley.models import *

data_disclaimer = """ "These files are being provided as quickly as possible--but we cannot guarantee their accuracy. For more information, see: http://reporting.sunlightfoundation.com/super-pac/data/about/year-end/2011/ Please note that contributions in these files are as of the most recent filing deadline--which is Feb. 29 for monthly filers, but Dec. 31, 2011 for quarterly filers. Presidential spending totals may not match up to overall spending totals, which may include independent expenditures made in support of congressional candidates. Independent expenditures are not comparable to the itemized disbursements found in PACs year-end reports. For more on independent expenditures see here: http://www.fec.gov/pages/brochures/indexp.shtml" """

hybrid_superpac_disclaimer ="\"Hybrid\" super PACs--committees that have separate accounts for \"hard\" and \"soft\" money, are not included. For a list of these committees, see <a href=\"http://www.fec.gov/press/press2011/2012PoliticalCommitteeswithNon-ContributionAccounts.shtml\">here</a>."

def generic_csv(filename, fields, rows):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    writer = csv.writer(response)
    writer.writerow([data_disclaimer])
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
        
def superpac_presidential_chart(request):
    
    superpacs_with_presidential_spending = IEOnlyCommittee.objects.filter(total_presidential_indy_expenditures__gte=10)
    total_spending = superpacs_with_presidential_spending.aggregate(total_spent=Sum('total_presidential_indy_expenditures'))
    return render_to_response('rebuckley/superpachack_chart.html',
                              {'superpacs':superpacs_with_presidential_spending,
                              'total':total_spending})
                              
def superpac_chart(request):

    superpacs_spending = IEOnlyCommittee.objects.filter( Q(total_indy_expenditures__gte=1) | Q(has_contributions=True) | Q(cash_on_hand__gt=100))
    return render_to_response('rebuckley/superpachack_chartall.html',
                            {'superpacs':superpacs_spending})  
                            
def expenditure_list(request, ieonlycommittee_id):
    committee = get_object_or_404(IEOnlyCommittee, fec_id=ieonlycommittee_id)
    committee_master = get_object_or_404(Committee, fec_id=ieonlycommittee_id)
    expenditures = Expenditure.objects.filter(committee=committee_master, is_superpac=True).filter(superceded_by_amendment=False)
    return render_to_response('rebuckley/superpachack_committee_spending_detail.html',
                            {'committee':committee, 
                            'committee_master':committee_master,
                            'expenditures':expenditures})
                            
                            
def expenditure_csv(request, ieonlycommittee_id):
    committee = get_object_or_404(IEOnlyCommittee, fec_id=ieonlycommittee_id)
    committee_master = get_object_or_404(Committee, fec_id=ieonlycommittee_id)
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(committee=committee_master, committee__is_superpac=True).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number', 'unmatched amendment' ]
    rows = []
    file_name = committee.slug + "_expenditures.csv"
    
    for ie in expenditures:
        rows.append([committee.fec_name, committee.fec_id, ie.candidate_name, ie.support_or_oppose(), ie.candidate.fec_id, ie.candidate.party, ie.candidate.office, ie.candidate.district, ie.candidate.state(), ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number, ie.unmatched_amendment() ])
    return generic_csv(file_name, fields, rows) 
    
def all_expenditures_csv(request):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(committee__is_superpac=True).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number', 'unmatched amendment' ]
    rows = []
    file_name =  "all_expenditures.csv"

    for ie in expenditures:
        rows.append([ie.committee.name, ie.committee.fec_id, ie.candidate_name, ie.support_or_oppose(), ie.candidate.fec_id, ie.candidate.party, ie.candidate.office, ie.candidate.district, ie.candidate.state(), ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number, ie.unmatched_amendment() ])
    return generic_csv(file_name, fields, rows)     
    
def expenditure_csv_state(request, state):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(state=state, committee__is_superpac=True).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number', 'unmatched amendment' ]
    rows = []
    file_name = state + "_expenditures.csv"

    for ie in expenditures:
        rows.append([ie.committee.name, ie.committee.fec_id, ie.candidate_name, ie.support_or_oppose(), ie.candidate.fec_id, ie.candidate.party, ie.candidate.office, ie.candidate.district, ie.candidate.state(), ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number, ie.unmatched_amendment() ])
    return generic_csv(file_name, fields, rows)    


def expenditure_csv_race(request, office, state, district):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(office=office, committee__is_superpac=True).filter(superceded_by_amendment=False)
    if (office in ('H', 'S')):
        expenditures = expenditures.filter(candidate__state_race=state)
    if (office == 'H'):
        expenditures = expenditures.filter(candidate__district=district)    
    
    fields = ['Spending Committee', 'Spending Committee ID', 'Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number', 'unmatched amendment' ]
    rows = []
    file_name = office + "_" + state + "_" + district + "_expenditures.csv"

    for ie in expenditures:
        rows.append([ie.committee.name, ie.committee.fec_id, ie.candidate_name, ie.support_or_oppose(), ie.candidate.fec_id, ie.candidate.party, ie.candidate.office, ie.candidate.district, ie.candidate.state(), ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number, ie.unmatched_amendment() ])
    return generic_csv(file_name, fields, rows)
    
def contribs_list(request, ieonlycommittee_id):
    committee = get_object_or_404(IEOnlyCommittee, fec_id=ieonlycommittee_id)
    contributions = Contribution.objects.filter(fec_committeeid=ieonlycommittee_id, superceded_by_amendment=False)
    return render_to_response('rebuckley/superpachack_committee_contrib_detail.html',
                            {'committee':committee, 
                            'contributions':contributions})
                            
def contribs_csv(request, ieonlycommittee_id):                            
    committee = get_object_or_404(IEOnlyCommittee, fec_id=ieonlycommittee_id)
    contributions = Contribution.objects.filter(fec_committeeid=ieonlycommittee_id, superceded_by_amendment=False)
    fields = ['Donor Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = committee.slug + "_donors.csv"

    for c in contributions:
        rows.append([c.contrib_source(), committee.fec_name, ieonlycommittee_id, c.contrib_org, c.contrib_last, c.contrib_first, c.contrib_city, c.contrib_state, c.contrib_occupation, c.contrib_employer, c.contrib_amt, c.contrib_date, c.transaction_id, c.filing_number])
    return generic_csv(file_name, fields, rows)
    
def state_contribs_csv(request, state):                            
    contributions = Contribution.objects.filter(contrib_state=state.upper(), superceded_by_amendment=False)
    fields = ['Donor Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = state + "_donors.csv"

    for c in contributions:
        rows.append([ c.contrib_source(), c.superpac.fec_name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.transaction_id, c.filing_number])
    return generic_csv(file_name, fields, rows)        
                                 
                                 
def all_contribs_csv(request):                            
    contributions = Contribution.objects.filter(superceded_by_amendment=False)
    fields = ['Donor Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = "all_donors.csv"

    for c in contributions:
        name = ''
        if (c.committee):
            name = c.committee.fec_name
        
        rows.append([ c.contrib_source(), c.superpac.fec_name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.transaction_id, c.filing_number])
    return generic_csv(file_name, fields, rows)  
    
    
## New views on old-style templates:

# about is on it's own template
def about(request):
    return render_to_response('rebuckley/about.html',
                            {})                                   

def all_superpacs(request):
    return redirect("/outside-spending/super-pacs/", permanent=True)

def presidential_superpacs(request):
    return redirect("/outside-spending/super-pacs/", permanent=True)
    

def committee_detail(request,slug, ieonlycommittee_id):
    newurl = "/outside-spending/committee/%s/%s/" % (slug, ieonlycommittee_id)
    return redirect(newurl, permanent=True)

def races(request):
    return redirect("/outside-spending/races/", permanent=True)


def race_detail(request, office, state, district):
    newurl = "/outside-spending/race_detail/%s/%s/%s/" % (office, state, district)
    return redirect(newurl, permanent=True)
    
def candidates(request):
    return redirect("/outside-spending/candidates/", permanent=True)
                            
def states(request):
    return redirect("/outside-spending/states/", permanent=True)

def dollarify(num):
    if num:
        return "$" + str(intcomma(num))
    else: 
        return ""

def states_csv(request):
    states = State_Aggregate.objects.filter(total_ind_exp__gt=0)
    fields = ['state','state_full', 'total', 'total_presidential','recent_presidential', 'house', 'senate']
    rows = []
    file_name = "states_summary.csv"

    for c in states:
        
        rows.append([c.state, c,dollarify(c.total_ind_exp),dollarify(c.total_pres_ind_exp), dollarify(c.recent_pres_exp), dollarify(c.total_house_ind_exp), dollarify(c.total_senate_ind_exp)])
    return generic_csv_headless(file_name, fields, rows)  

def presidential_state_summary(request, state):
    newurl = "/outside-spending/president-state-detail/%s/" % (state)
    return redirect(newurl, permanent=True) 

def state_detail(request, state_abbreviation):
    newurl = "/outside-spending/state/%s/" % (state_abbreviation)
    return redirect(newurl, permanent=True)

def ies(request):
    return redirect("/outside-spending/independent-expenditures/", permanent=True)

def candidate_detail(request, slug, candidate_id):
    newurl = "/outside-spending/candidate/%s/%s/" % (slug, candidate_id)
    return redirect(newurl, permanent=True)                           

def file_downloads(request):
    return redirect("/outside-spending/file-downloads/", permanent=True)

def complete_superpac_list(request):
    return redirect("/outside-spending/complete-list/", permanent=True)
                            
def organizational_superpac_contribs(request):
    return redirect("/outside-spending/super-pacs/donating-organizations/", permanent=True)