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
    
    monthly_ie_summary = summarize_monthly(superpac_ies, today)
    
    superpac_contribs = Expenditure.objects.filter(superceded_by_amendment=False, committee__is_superpac=True).extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))
    
    monthly_contrib_data = Contribution.objects.filter(committee__is_superpac=True, superceded_by_amendment=False).extra(select={'year': 'EXTRACT(year FROM contrib_date)','month': 'EXTRACT(month FROM contrib_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('contrib_amt'))
    
    # hack to only show contribs after the 20th of the month--which misses quarterly contribs, but... 
    m = datetime.timedelta(days=20)
    monthly_contrib_summary = summarize_monthly(monthly_contrib_data, today-m)
    print monthly_contrib_summary
    
    return {
    'has_series1':True,
    'series1_data':monthly_ie_summary,
    'series1_title':'MONTHLY INDEPENDENT EXPENDITURES',
    'has_series2':True,
    'series2_title':'MONTHLY CONTRIBUTIONS',
    'series2_data':monthly_contrib_summary,
    'return_div':div_to_return,
    }



@register.inclusion_tag('outside_spending/chart_templatetag.html')  
def noncommittee_spending(div_to_return):

    noncommittee_ies = Expenditure.objects.filter(superceded_by_amendment=False,committee__ctype='I').extra(select={'year': 'EXTRACT(year FROM expenditure_date)','month': 'EXTRACT(month FROM expenditure_date)'}).values_list('year', 'month').order_by('year', 'month').annotate(Sum('expenditure_amount'))

    today = datetime.datetime.today()

    monthly_ie_summary = summarize_monthly(noncommittee_ies, today)

    
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

    monthly_ie_summary = summarize_monthly(nonparty_ies, today)


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

    monthly_ie_summary = summarize_monthly(party_ies, today)


    return {
    'has_series1':True,
    'series1_data':monthly_ie_summary,
    'series1_title':'PARTY COMMITTEE INDEPENDENT EXPENDITURES',
    'has_series2':False,
    'return_div':div_to_return,
    }    