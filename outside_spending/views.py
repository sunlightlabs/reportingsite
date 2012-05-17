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
from outside_spending.models import Scrape_Time

STATE_CHOICES = dict(STATE_CHOICES)
most_recent_scrape=Scrape_Time.objects.all().order_by('-run_time')[0]

from outside_spending.models import *

data_disclaimer = """ These files are preliminary and current through %s but we cannot guarantee their accuracy. For more information, see: http://reporting.sunlightfoundation.com/outside-spending/about/ Please note that contributions in these files are as of the most recent filing deadline. Independent expenditures are not comparable to the itemized disbursements found in PAC's year-end reports. For more on independent expenditures see here: http://www.fec.gov/pages/brochures/indexp.shtml """ % (most_recent_scrape.run_time)

hybrid_superpac_disclaimer ="\"Hybrid\" super PACs--committees that have separate accounts for \"hard\" and \"soft\" money, are not included. For a list of these committees, see <a href=\"http://www.fec.gov/press/press2011/2012PoliticalCommitteeswithNon-ContributionAccounts.shtml\">here</a>."

electioneering_details="""<a target="_new" href="http://www.fec.gov/pages/brochures/electioneering.shtml">Electioneering communications</a>  are broadcast communications not otherwise
reported as independent expenditures. Electioneering communication
reports do not state whether the communication was in support of or in
opposition to the candidate, and they sometimes refer to multiple
candidates."""

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
            
        rows.append([committee_name, committee_fec_id, superpac_status, hybrid_status, ie.candidate_name, ie.support_or_oppose(), candidate_fec_id, candidate_party, candidate_office, candidate_district, candidate_state, ie.expenditure_amount, ie.state, ie.expenditure_date, ie.payee, ie.expenditure_purpose, ie.transaction_id, ie.filing_number ])
        
    return rows

def expenditure_csv(request, committee_id):
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id)
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(committee=committee).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Hybrid PAC?','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = committee.slug + "_expenditures.csv"
    return generic_csv(file_name, fields, rows) 

def all_expenditures_csv(request):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Hybrid PAC?','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name =  "all_expenditures.csv"
            
    return generic_csv(file_name, fields, rows)     

def expenditure_csv_state(request, state):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(state=state).filter(superceded_by_amendment=False)
    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Hybrid PAC?','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = state + "_expenditures.csv"
    return generic_csv(file_name, fields, rows)    


def expenditure_csv_race(request, office, state, district):
    expenditures = Expenditure.objects.select_related("committee", "candidate").filter(office=office).filter(superceded_by_amendment=False)
    if (office in ('H', 'S')):
        expenditures = expenditures.filter(candidate__state_race=state)
    if (office == 'H'):
        expenditures = expenditures.filter(candidate__district=district)    

    fields = ['Spending Committee', 'Spending Committee ID', 'Superpac?', 'Hybrid PAC?','Candidate supported / opposed', 'support/oppose', 'Candidate ID', 'Candidate Party', 'Candidate Office', 'Candidate District', 'Candidate State', 'Expenditure amount', 'Expenditure state', 'Expenditure date', 'Recipient', 'Purpose', 'Transaction ID', 'Filing Number' ]
    rows = make_expenditure_list(expenditures)
    file_name = office + "_" + state + "_" + district + "_expenditures.csv"
    return generic_csv(file_name, fields, rows)

def contribs_csv(request, committee_id):                            
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id)
    contributions = Contribution.objects.filter(fec_committeeid=committee_id, superceded_by_amendment=False)
    fields = ['Donor Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = committee.slug + "_donors.csv"

    for c in contributions:
        rows.append([c.contrib_source(), committee.name, committee_id, c.contrib_org, c.contrib_last, c.contrib_first, c.contrib_city, c.contrib_state, c.contrib_occupation, c.contrib_employer, c.contrib_amt, c.contrib_date, c.transaction_id, c.filing_number])
    return generic_csv(file_name, fields, rows)

def state_contribs_csv(request, state):                            
    contributions = Contribution.objects.filter(contrib_state=state.upper(), superceded_by_amendment=False)
    fields = ['Donor Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = state + "_donors.csv"

    for c in contributions:
        rows.append([ c.contrib_source(), c.committee.name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.transaction_id, c.filing_number])
    return generic_csv(file_name, fields, rows)        


def all_contribs_csv(request):                            
    contributions = Contribution.objects.filter(superceded_by_amendment=False)
    fields = ['Donor Type','Receiving Super PAC', 'Super PAC ID', 'Donating organization','Donor Last', 'Donor First', 'Donor City', 'Donor State', 'Donor Occupation', 'Employer', 'Amount', 'Date', 'Transaction ID', 'Filing Number']
    rows = []
    file_name = "all_donors.csv"

    for c in contributions:
        name = ''
        if (c.committee):
            name = c.committee.name

        rows.append([ c.contrib_source(), c.committee.name, c.fec_committeeid, c.contrib_org.replace('"',''), c.contrib_last.replace('"',''), c.contrib_first.replace('"',''), c.contrib_city.replace('"',''), c.contrib_state.replace('"',''), c.contrib_occupation.replace('"',''), c.contrib_employer.replace('"',''), c.contrib_amt, c.contrib_date, c.transaction_id, c.filing_number])
    return generic_csv(file_name, fields, rows)
    
    

def all_superpacs(request):
    explanatory_text = "This table shows all independent expenditure-only committees--better known as super PACS--that have raised at least $10,000 since the beginning of 2011. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site. For the much longer list of <a href='/outside-spending/super-pacs/complete-list/'>all superpacs</a> click <a href='/outside-spending/super-pacs/complete-list/'>here</a>."

    superpacs = Committee_Overlay.objects.filter(total_contributions__gte=10000, is_superpac=True)
    total = superpacs.aggregate(total=Sum('total_indy_expenditures'))
    total_amt = total['total']

    return render_to_response('outside_spending/superpac_list.html',
                            {'explanatory_text':explanatory_text, 
                            'superpacs':superpacs, 
                            'total_amt':total_amt}) 

def complete_superpac_list(request):
    superpacs = Committee_Overlay.objects.filter(is_superpac=True).order_by('total_indy_expenditures')
    explanatory_text= 'This is a list of all super PACs.'
    return render_to_response('outside_spending/superpac_show_all.html',
                            {'superpacs':superpacs,
                            'explanatory_text':explanatory_text,
                            })  
def committee_detail(request,committee_id):
    committee = get_object_or_404(Committee_Overlay, fec_id=committee_id)
    expenditures = Expenditure.objects.filter(committee=committee).filter(superceded_by_amendment=False).select_related('committee', 'candidate')
    contributions = Contribution.objects.filter(fec_committeeid=committee_id, superceded_by_amendment=False)
    candidates_supported = Pac_Candidate.objects.filter(committee=committee)
    explanatory_text = 'This table shows the overall total amount spent by this group supporting or opposing federal candidates in independent expenditures in the 2012 election cycle.'
    explanatory_text_details = 'This table shows the total independent expenditure by this group supporting or opposing federal candidates in the 2012 election cycle. To view a more detailed file of this spending, <a href=\"%s\">click here</a>.' % (committee.superpachackcsv())
    explanatory_text_contribs = 'This table shows all contributions made to this group during the 2012 campaign cycle, as of %s. To view a more detailed file of this spending, <a href=\"%s\">click here</a>.' % (committee.cash_on_hand_date,committee.superpachackdonorscsv())
    
    ecs = Electioneering_93.objects.select_related("target", "target__candidate").filter(superceded_by_amendment=False, fec_id=committee_id).order_by('-exp_date')
    ec_total_dict = ecs.aggregate(total=Sum('exp_amo'))
    ec_total = ec_total_dict['total']
    
    
    return render_to_response('outside_spending/committee_detail.html',
                            {'committee':committee, 
                            'expenditures':expenditures,
                            'contributions':contributions, 
                            'candidates':candidates_supported,
                            'explanatory_text':explanatory_text,
                            'explanatory_text_details':explanatory_text_details,
                            'explanatory_text_contribs':explanatory_text_contribs,
                            'ecs':ecs,
                            'ec_explanation':electioneering_details,
                            'ec_total':ec_total
                            })   
                            

def presidential_superpacs(request):
    explanatory_text = "This table shows all independent expenditure-only committees--better known as super PACs--that have spent more than $1,000 in independent expenditures in support of a presidential candidate during the 2012 election cycle. Click on the 'FEC filings' links to see the original filings on the Federal Election Commission's web site."

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
    explanatory_text = 'This is a list of groups that have made independent expenditures for or against a presidential candidate in the state of ' + state_name + '.'
    explanatory_text_details = 'This is a list all independent expenditures made for or against a presidential candidate in the state of ' + state_name + '.'
    
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
    explanatory_text_details = 'This is a list of all super PAC independent expenditures made for or against this candidate.'
    superpacs = Pac_Candidate.objects.filter(candidate=candidate)
    expenditures = Expenditure.objects.filter(superceded_by_amendment=False, candidate=candidate).select_related("committee")
    
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
    explanatory_text= 'This table lists the sums of independent expenditures and electioneering communications reported to have been made in each state during the 2012 election cycle. While FEC rules require super PACs and other political groups to designate the state each independent expenditure is made in, many expenditures--particularly those spread across multiple states--are missing this information. Therefore, the totals on this page will not match overall totals found elsewhere on this site. For downloadable state-by-state files, see the <a href="/outside-spending/file-downloads/">downloads page</a>. ' + electioneering_details
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

    explanatory_text= 'For a downloadable .csv file of this information, <a href="/outside-spending/csv/state/expenditures/%s/">click here</a>.</p><p>This table lists the total of all independent expenditures and electioneering communications made during the 2012 election cycle by race. While FEC rules require super PACs and other political groups to designate the state each independent expenditure is made in, many expenditures--particularly those spread across multiple states--are missing this information. Therefore, the totals on this page will not match overall totals found elsewhere on this site.' % (state_abbreviation)
    return render_to_response('outside_spending/state_detail.html',
                            {'races':races, 
                            'state_name':state_name,
                            'candidates':candidates,
                            'explanatory_text':explanatory_text,
                            'this_state':this_state
                            })


def ies(request):
    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=14)
    ies = Expenditure.objects.select_related("committee", "candidate").filter(superceded_by_amendment=False, expenditure_date__gte=two_weeks_ago).order_by('-expenditure_date')
    explanatory_text= 'This page shows independent expenditures made in the last two weeks.'
    return render_to_response('outside_spending/expenditure_list.html',
                            {'ies':ies, 
                            'explanatory_text':explanatory_text,
                            })


def ecs(request):
    #today = datetime.date.today()
    #two_weeks_ago = today - datetime.timedelta(days=14)
    ecs = Electioneering_93.objects.select_related("target", "target__candidate").filter(superceded_by_amendment=False).order_by('-exp_date')
    #explanatory_text= 'This page shows electioneering communications.'
    return render_to_response('outside_spending/electioneering_list.html',
                            {'ecs':ecs, 
                            'explanatory_text':electioneering_details
                            })



def organizational_superpac_contribs(request):
    contribs = Contribution.objects.select_related("committee").filter(committee__isnull=False, superceded_by_amendment=False).exclude(contrib_org='').filter(line_type__in=['SA11AI', 'SA15'])


    total = contribs.aggregate(total=Sum('contrib_amt'))
    total_amt = total['total']

    explanatory_text= 'This is a list of all contributions to super PACs from organizations, including money received as operating expense offsets. These offsets, which are marked with an asterisk below, often include administrative overhead paid by a related organization, though sometimes include refund payments. This list does not include contributions from corporate--or any other--PACs. '
    return render_to_response('outside_spending/organizational_contribs.html',
                            {'contribs':contribs,
                            'total_amt':total_amt,
                            'explanatory_text':explanatory_text,
                            })
                            
def file_downloads(request):
    committees = Committee_Overlay.objects.all().order_by('name')
    states = State_Aggregate.objects.filter(total_ind_exp__gt=0).order_by('state')
    races = Race_Aggregate.objects.filter(total_ind_exp__gt=0).order_by('state', 'office', 'district')

    return render_to_response('outside_spending/file_downloads.html',
                            {'committees':committees, 
                            'states':states,
                            'races':races,
                            })  
# Not built yet! redirect for the time being
# I think the projecst page points at this, so don't want url to break                        
def overview(request):
    return redirect("/outside-spending/super-pacs/")


@cache_page(60 * 15)                              
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

    
    contribs = Contribution.objects.filter(line_type__in=['SA11AI', 'SA15'])
    total_contribs_amt = contribs.aggregate(total=Sum('contrib_amt'))
    total_contribs = total_contribs_amt['total']
    
    list_all_ies = Expenditure.objects.filter(superceded_by_amendment=False).select_related("candidate")
    total_ies = list_all_ies.aggregate(total=Sum('expenditure_amount'))['total']
    pres_ies = list_all_ies.filter(candidate__office='P').aggregate(total=Sum('expenditure_amount'))['total']
    house_ies = list_all_ies.filter(candidate__office='H').aggregate(total=Sum('expenditure_amount'))['total']
    senate_ies = list_all_ies.filter(candidate__office='S').aggregate(total=Sum('expenditure_amount'))['total']
    supporting_ies = list_all_ies.filter(support_oppose='S').aggregate(total=Sum('expenditure_amount'))['total']
    opposing_ies = list_all_ies.filter(support_oppose='O').aggregate(total=Sum('expenditure_amount'))['total']
    
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
        'total_organizational':total_organizational})
        
def recent_fec_filings(request):
    
    update_time=Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    filings = unprocessed_filing.objects.all().order_by('-filing_number')[:100]
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

    filings = unprocessed_filing.objects.filter(form_type__in=['F5A', 'F5N', 'F24A', 'F24N']).order_by('-filing_number')[:100]
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

    filings = unprocessed_filing.objects.filter(fec_id__in=['C00431171', 'C00496497', 'C00496034', 'C00495820', 'C00010603', 'C00042366', 'C00000935', 'C00003418', 'C00027466', 'C00075820', 'C00431445']).order_by('-filing_number')[:100]
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

    filings = unprocessed_filing.objects.filter(fec_id__in=['C00431171', 'C00496497', 'C00496034', 'C00495820', 'C00010603', 'C00042366', 'C00000935', 'C00003418', 'C00027466', 'C00075820', 'C00431445'], form_type__in=['F3XN', 'F3N', 'F3PN']).order_by('-filing_number')[:100]
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
    
    filings = unprocessed_filing.objects.filter(is_superpac=True).order_by('-filing_number')[:100]
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

    filings = unprocessed_filing.objects.filter(is_superpac=True, form_type='F3XN').order_by('-filing_number')[:100]
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
    title="Recent FEC Filings"
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
    title="Recent Independent Expenditure Filings"
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
    title="Notable PAC Filings"
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
    title="Notable PAC Filings"
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
    title='Super PAC Filings'
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
    title='Super PAC Filings'
    explanatory_text="These are recent electronic monthly / quarterly reports from super PACs."

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

    return render_to_response('mobile_test/committee_search.html',
        {
        'committees':committees,
        }
    )    
def subscribe_to_alerts(request):
    
    return render_to_response('outside_spending/subscribe.html',
        {}
    )
       