import datetime
from django.template import Library
from outside_spending.models import Expenditure, Contribution
from outside_spending.views import summarize_monthly
from django.db.models import Sum

register = Library()

# assumes hardcoded div of 
@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def superpac_chart(div_to_return):
    
    superpac_ies = Expenditure.objects.filter(superceded_by_amendment=False, committee__is_superpac=True).extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))
    
    today = datetime.datetime.today()
    
    monthly_ie_summary = summarize_monthly(superpac_ies, today, True)
    
    superpac_contribs = Expenditure.objects.filter(superceded_by_amendment=False, committee__is_superpac=True).extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))
    
    monthly_contrib_data = Contribution.objects.filter(committee__is_superpac=True, superceded_by_amendment=False, line_type__in=['SA11A1', 'SA11B', 'SA11C', 'SA12', 'SA15']).extra(select={'year': 'EXTRACT(year FROM contrib_date)','month': 'EXTRACT(month FROM contrib_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('contrib_amt'))
    
    # hack to only show contribs after the 20th of the month--which misses quarterly contribs, but... 
    m = datetime.timedelta(days=17)
    monthly_contrib_summary = summarize_monthly(monthly_contrib_data, today-m)
    print monthly_contrib_summary
    
    return {
    'has_series1':True,
    'series1_data':monthly_ie_summary,
    'series1_title':'MONTHLY SUPER PAC INDEPENDENT EXPENDITURES',
    'has_series2':True,
    'series2_title':'MONTHLY SUPER PAC CONTRIBUTIONS',
    'series2_data':monthly_contrib_summary,
    'return_div':div_to_return,
    }

@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def all_ies_chart(div_to_return):

    all_ies = Expenditure.objects.filter(superceded_by_amendment=False).extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_summary = summarize_monthly(all_ies, today, True)


    return {
    'has_series1':True,
    'series1_data':monthly_ie_summary,
    'series1_title':'ALL INDEPENDENT EXPENDITURES',
    'has_series2':False,
    'return_div':div_to_return,
    }

@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def noncommittee_spending(div_to_return):

    noncommittee_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__ctype='I').extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_summary = summarize_monthly(noncommittee_ies, today, True)

    
    return {
    'has_series1':True,
    'series1_data':monthly_ie_summary,
    'series1_title':'NONCOMMITTEE INDEPENDENT EXPENDITURES',
    'has_series2':False,
    'return_div':div_to_return,
    }
    
@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def nonparty_spending(div_to_return):

    nonparty_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__ctype__in=('N', 'Q')).extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_summary = summarize_monthly(nonparty_ies, today, True)


    return {
    'has_series1':True,
    'series1_data':monthly_ie_summary,
    'series1_title':'NON-PARTY INDEPENDENT EXPENDITURES',
    'has_series2':False,
    'return_div':div_to_return,
    }    
    
    
@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def party_spending(div_to_return):

    party_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__ctype__in=('Y', 'Z')).extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_summary = summarize_monthly(party_ies, today, True)


    return {
    'has_series1':True,
    'series1_data':monthly_ie_summary,
    'series1_title':'PARTY COMMITTEE INDEPENDENT EXPENDITURES',
    'has_series2':False,
    'return_div':div_to_return,
    } 
    
@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def superpac_partisan(div_to_return):

    r_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__political_orientation='R').extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))
    
    d_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__political_orientation='D').extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_r_summary = summarize_monthly(r_ies, today, True)
    monthly_ie_d_summary = summarize_monthly(d_ies, today, True)

    return {
    'has_series1':True,
    'series2_data':monthly_ie_r_summary,
    'series2_title':'REPUBLICAN SUPERPAC SPENDING',
    'has_series2':True,
    'series1_data':monthly_ie_d_summary,
    'series1_title':'DEMOCRATIC SUPERPAC SPENDING',
    'return_div':div_to_return,
    }
    
@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def superpac_partisan_primary(div_to_return):

    r_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__political_orientation='R', election_type="P").extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    d_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__political_orientation='D', election_type="P").extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_r_summary = summarize_monthly(r_ies, today, True)
    monthly_ie_d_summary = summarize_monthly(d_ies, today, True)

    return {
    'has_series1':True,
    'series2_data':monthly_ie_r_summary,
    'series2_title':'PRIMARY ELECTION REPUBLICAN SUPERPAC SPENDING',
    'has_series2':True,
    'series1_data':monthly_ie_d_summary,
    'series1_title':'PRIMARY ELECTION DEMOCRATIC SUPERPAC SPENDING',
    'return_div':div_to_return,
    }

@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def superpac_partisan_general(div_to_return):

    r_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__political_orientation='R', election_type="G").extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    d_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__political_orientation='D', election_type="G").extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_r_summary = summarize_monthly(r_ies, today, True)
    monthly_ie_d_summary = summarize_monthly(d_ies, today, True)

    return {
    'has_series1':True,
    'series2_data':monthly_ie_r_summary,
    'series2_title':'GENERAL ELECTION REPUBLICAN SUPERPAC SPENDING',
    'has_series2':True,
    'series1_data':monthly_ie_d_summary,
    'series1_title':'GENERAL ELECTION DEMOCRATIC SUPERPAC SPENDING',
    'return_div':div_to_return,
    }
    
@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def superpac_partisan_general_presidential(div_to_return):

    all_pres_general_ies = Expenditure.objects.filter(superceded_by_amendment=False,candidate__office='P', election_type="G").select_related('committee')
    
    r_ies = all_pres_general_ies.filter(committee__political_orientation='R').extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    d_ies = all_pres_general_ies.filter(committee__political_orientation='D').extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_r_summary = summarize_monthly(r_ies, today, True)
    monthly_ie_d_summary = summarize_monthly(d_ies, today, True)

    return {
    'has_series1':True,
    'series2_data':monthly_ie_r_summary,
    'series2_title':'PRESIDENTIAL GENERAL ELECTION REPUBLICAN SUPERPAC SPENDING',
    'has_series2':True,
    'series1_data':monthly_ie_d_summary,
    'series1_title':'PRESIDENTIAL GENERAL ELECTION DEMOCRATIC SUPERPAC SPENDING',
    'return_div':div_to_return,
    }    
    
@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def superpac_partisan_contribs(div_to_return):
    
    today = datetime.datetime.today()
    m = datetime.timedelta(days=20)
    
    monthly_r_contribs = Contribution.objects.filter(committee__is_superpac=True, superceded_by_amendment=False, committee__political_orientation='R', line_type__in=['SA11A1', 'SA11B', 'SA11C', 'SA12', 'SA15']).extra(select={'year': 'EXTRACT(year FROM contrib_date)','month': 'EXTRACT(month FROM contrib_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('contrib_amt'))
    
    # hack to only show contribs after the 20th of the month--which misses quarterly contribs, but... 
    monthly_r_contrib_summary = summarize_monthly(monthly_r_contribs, today-m)
    
    monthly_d_contribs = Contribution.objects.filter(committee__is_superpac=True, superceded_by_amendment=False, committee__political_orientation='D', line_type__in=['SA11A1', 'SA11B', 'SA11C', 'SA12', 'SA15']).extra(select={'year': 'EXTRACT(year FROM contrib_date)','month': 'EXTRACT(month FROM contrib_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('contrib_amt'))

    monthly_d_contrib_summary = summarize_monthly(monthly_d_contribs, today-m)
    
        
    return {
    'has_series1':True,
    'series1_data':monthly_d_contrib_summary,
    'series1_title':'MONTHLY CONTRIBUTIONS - DEMOCRATIC SUPERPACS',
    'has_series2':True,
    'series2_title':'MONTHLY CONTRIBUTIONS - REPUBLICAN SUPERPACS',
    'series2_data':monthly_r_contrib_summary,
    'return_div':div_to_return,
    }        