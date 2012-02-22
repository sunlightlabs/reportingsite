# Create your views here.
import csv
import datetime

from django.views.decorators.cache import cache_page
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.db.models import Sum
from django.db.models import Q
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.humanize.templatetags.humanize import intcomma

STATE_CHOICES = dict(STATE_CHOICES)

from rebuckley.models import *

data_disclaimer = """ "These files are being provided as quickly as possible--but we cannot guarantee their accuracy. For more information, see: http://reporting.sunlightfoundation.com/super-pac/data/about/year-end/2011/ Please note that contributions in these files are as of the most recent filing deadline--whic is Jan. 31 for monthly filers, but Dec. 31, 2011 for quarterly filers. Presidential spending totals may not match up to overall spending totals, which may include independent expenditures made in support of congressional candidates. Independent expenditures are not comparable to the itemized disbursements found in PACs year-end reports. For more on independent expenditures see here: http://www.fec.gov/pages/brochures/indexp.shtml" """

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
    expenditures = Expenditure.objects.filter(committee=committee_master, committee__is_superpac=True).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number', 'unmatched amendment' ]
    rows = []
    file_name = committee.slug + "_expenditures.csv"
    
    for ie in expenditures:
        rows.append([committee.fec_name, committee.fec_id, ie.candidate_name, ie.support_or_oppose(), ie.candidate.fec_id, ie.candidate.party, ie.candidate.office, ie.candidate.district, ie.candidate.state(), ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number, ie.unmatched_amendment() ])
    return generic_csv(file_name, fields, rows) 
    
def all_expenditures_csv(request):
    expenditures = Expenditure.objects.filter(committee__is_superpac=True).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number', 'unmatched amendment' ]
    rows = []
    file_name =  "all_expenditures.csv"

    for ie in expenditures:
        rows.append([ie.committee.name, ie.committee.fec_id, ie.candidate_name, ie.support_or_oppose(), ie.candidate.fec_id, ie.candidate.party, ie.candidate.office, ie.candidate.district, ie.candidate.state(), ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number, ie.unmatched_amendment() ])
    return generic_csv(file_name, fields, rows)     
    
def expenditure_csv_state(request, state):
    expenditures = Expenditure.objects.filter(state=state, committee__is_superpac=True).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number', 'unmatched amendment' ]
    rows = []
    file_name = state + "_expenditures.csv"

    for ie in expenditures:
        rows.append([ie.committee.name, ie.committee.fec_id, ie.candidate_name, ie.support_or_oppose(), ie.candidate.fec_id, ie.candidate.party, ie.candidate.office, ie.candidate.district, ie.candidate.state(), ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number, ie.unmatched_amendment() ])
    return generic_csv(file_name, fields, rows)    


def expenditure_csv_race(request, office, state, district):
    expenditures = Expenditure.objects.filter(office=office, committee__is_superpac=True).filter(superceded_by_amendment=False)
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
    explanatory_text = "This table shows all independent expenditure-only committees--better known as super PACS--that have raised at least $10,000 since the beginning of 2011. For a complete list of all super PACS that includes the many that have not raised any money see <a href=\"http://www.fec.gov/press/press2011/ieoc_alpha.shtml\">here</a>. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site."
    
    superpacs = IEOnlyCommittee.objects.filter(total_contributions__gte=10000)
    total = superpacs.aggregate(total=Sum('total_indy_expenditures'))
    total_amt = total['total']

    return render_to_response('rebuckley/superpac_list.html',
                            {'explanatory_text':explanatory_text, 
                            'superpacs':superpacs, 
                            'total_amt':total_amt})
                                
def presidential_superpacs(request):
    explanatory_text = "This table shows all independent expenditure-only committees--better known as super PACs--that have made independent expenditures in support of a presidential candidate during the 2012 election cycle. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site."

    superpacs = IEOnlyCommittee.objects.filter(total_presidential_indy_expenditures__gte=10)
    total = superpacs.aggregate(total=Sum('total_presidential_indy_expenditures'))
    total_amt = total['total']    

    return render_to_response('rebuckley/presidential_superpac_list.html',
                            {'explanatory_text':explanatory_text, 
                            'superpacs':superpacs,
                            'total_amt':total_amt}) 
                            
                             
def committee_detail(request,ieonlycommittee_id):
    committee = get_object_or_404(IEOnlyCommittee, fec_id=ieonlycommittee_id)
    committee_master = get_object_or_404(Committee, fec_id=ieonlycommittee_id)
    expenditures = Expenditure.objects.filter(committee=committee_master).filter(superceded_by_amendment=False)
    contributions = Contribution.objects.filter(fec_committeeid=ieonlycommittee_id, superceded_by_amendment=False)
    candidates_supported = Pac_Candidate.objects.filter(committee=committee_master)
    explanatory_text = 'This table shows the overall total amount spent by this super PAC supporting or opposing federal candidates in independent expenditures in the 2012 election cycle.'
    explanatory_text_details = 'This table shows all independent expenditures made by this super PAC during the 2012 campaign cycle. To view a more detailed file of this spending, <a href=\"%s\">click here</a>.' % (committee.superpachackcsv())
    explanatory_text_contribs = 'This table shows all contributions made to this super PAC during the 2012 campaign cycle, as of %s. To view a more detailed file of this spending, <a href=\"%s\">click here</a>.' % (committee.cash_on_hand_date,committee.superpachackdonorscsv())
    return render_to_response('rebuckley/committee_detail.html',
                            {'committee':committee, 
                            'committee_master':committee_master,
                            'expenditures':expenditures,
                            'contributions':contributions, 
                            'candidates':candidates_supported,
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details,
                            'explanatory_text_contribs':explanatory_text_contribs
                            })
                            
def races(request):
    races = Race_Aggregate.objects.exclude(district__isnull=True)
    explanatory_text = "This page shows independent expenditures made by super PACS in the 2012 election cycle by race. Click on each race to see aggregate totals by candidate, and to get access to a downloadable file of all individual expenditures for this race."
    return render_to_response('rebuckley/race_list.html',
                            {'races':races, 
                            'explanatory_text':explanatory_text
                            })

def race_detail(request, office, state, district):
    race_aggregate = get_object_or_404(Race_Aggregate, office=office, state=state, district=district)
    candidate_pacs = Pac_Candidate.objects.filter(candidate__office=office, candidate__state_race=state, candidate__district=district)
    explanatory_text = "This table shows the total amount each super PAC made in independent expenditures to support or oppose a candidate in this race. For a downloadable file of this information, <a href=\"/super-pacs/csv/race/expenditures/%s/%s/%s/\">click here</a>." % (office, state, district)
    race_name = None
    if (office=='P'):
        race_name = 'President'
    elif office == 'S':
        race_name = '%s (Senate)' % state
    else:
        race_name='%s-%s (House)' % (state, district.lstrip('0'))
        
    return render_to_response('rebuckley/race_detail.html',
                            {'candidates':candidate_pacs, 
                            'explanatory_text':explanatory_text, 
                            'race_name':race_name,
                            'race_aggregate':race_aggregate
                            })  
def candidates(request):
    candidates = Candidate.objects.filter(total_expenditures__gte=10)
    explanatory_text= 'This table lists the total of all super PAC independent expenditures made to support or oppose federal candidates during the 2012 election cycle. Candidates not receiving opposition or support from super PACs are not shown.'
    return render_to_response('rebuckley/candidate_list.html',
                            {'candidates':candidates, 
                            'explanatory_text':explanatory_text,
                            })
                            
def states(request):
    states = State_Aggregate.objects.filter(total_ind_exp__gt=0)
    explanatory_text= 'This table lists the total of all super PAC independent expenditures reported to have been made in each state during the 2012 election cycle. While FEC rules require super PACs to designate the state each independent expenditure is made in, many expenditures--particularly those spread across multiple states--are missing this information. Therefore, the totals on this page will not match overall totals found elsewhere on this site. For downloadable state-by-state files, see the <a href="/super-pacs/file-downloads/">downloads page</a>.'
    return render_to_response('rebuckley/state_list.html',
                            {'states':states, 
                            'explanatory_text':explanatory_text,
                            }) 

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
    try:
        state_name = STATE_CHOICES[state]
    except KeyError:
        raise Http404
    
    state_pacs = President_State_Pac_Aggregate.objects.filter(state=state)
    
    expenditures = Expenditure.objects.filter(committee__is_superpac=True, superceded_by_amendment=False, state=state, office='P')
    explanatory_text = 'This is a list of super PACs that have made independent expenditures for or against a presidential candidate in the state of ' + state_name + '.'
    explanatory_text_details = 'This is a list all independent expenditures made by super PACs for or against a presidential candidate in the state of ' + state_name + '.'
    
    return render_to_response('rebuckley/state_presidential_detail.html',
                            {'state_pacs':state_pacs, 
                            'state_name':state_name,
                            'explanatory_text':explanatory_text,
                            'expenditures':expenditures,
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details
                            })
    

def state_detail(request, state_abbreviation):
    
    try:
        state_name = STATE_CHOICES[state_abbreviation]
    except KeyError:
        raise Http404
        

    races = Race_Aggregate.objects.filter(state__iexact=state_abbreviation).exclude(district__isnull=True)
    this_state = State_Aggregate.objects.get(state=state_abbreviation)
    
    candidates = Candidate.objects.filter(total_expenditures__gte=10, state_race__iexact=state_abbreviation)

    explanatory_text= 'For a downloadable .csv file of this information, <a href="/super-pacs/csv/state/expenditures/%s/">click here</a>.</p><p>This table lists the total of all super PAC independent expenditures made in each state during the 2012 election cycle by race. While FEC rules require super PACs to designate the state each independent expenditure is made in, many expenditures--particularly those spread across multiple states--are missing this information. Therefore, the totals on this page will not match overall totals found elsewhere on this site.' % (state_abbreviation)
    return render_to_response('rebuckley/state_detail.html',
                            {'races':races, 
                            'state_name':state_name,
                            'candidates':candidates,
                            'explanatory_text':explanatory_text,
                            'this_state':this_state
                            }) 
                            

                                                       
def ies(request):
    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=14)
    ies = Expenditure.objects.filter(committee__is_superpac=True, superceded_by_amendment=False, expenditure_date__gte=two_weeks_ago).order_by('-expenditure_date')
    explanatory_text= 'This page shows independent expenditures made by super PACs in the last two weeks.'
    return render_to_response('rebuckley/expenditure_list.html',
                            {'ies':ies, 
                            'explanatory_text':explanatory_text,
                            }) 

def candidate_detail(request, candidate_id):
    candidate = Candidate.objects.get(fec_id=candidate_id)
    explanatory_text= 'This is a list of all super PACs that have made independent expenditures supporting or opposing this candidate.'
    explanatory_text_details = 'This is a list of all super PAC independent expenditures made for or against this candidate.'
    superpacs = Pac_Candidate.objects.filter(candidate=candidate)
    expenditures = Expenditure.objects.filter(committee__is_superpac=True, superceded_by_amendment=False, candidate=candidate)
    return render_to_response('rebuckley/candidate_detail.html',
                            {'candidate':candidate, 
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details,
                            'superpacs':superpacs,
                            'expenditures':expenditures
                            })                               
                                                                                       

def file_downloads(request):
    superpacs = IEOnlyCommittee.objects.filter(total_indy_expenditures__gt=0).order_by('fec_name')
    states = State_Aggregate.objects.filter(total_ind_exp__gt=0).order_by('state')
    races = Race_Aggregate.objects.filter(total_ind_exp__gt=0).order_by('state', 'office', 'district')
    
    return render_to_response('rebuckley/file_downloads.html',
                            {'superpacs':superpacs, 
                            'states':states,
                            'races':races,
                            })                          