from django import template
from django.core.cache import cache
from reportingsite.millions.models import *

register = template.Library()

def filters():
    cache_key = 'millions_filters'

    filters = cache.get(cache_key)
    if filters:
        return filters

    baseq = Record.objects.filter(version_flag='F', recipient_role='P').exclude(status='x')
    recipient_state = baseq.values_list('recipient_state', flat=True).distinct().order_by('recipient_state')
    awarding_agency_name = baseq.values_list('awarding_agency_name', flat=True).distinct().order_by('awarding_agency_name')
    pop_state_cd = baseq.values_list('pop_state_cd', flat=True).distinct().order_by('pop_state_cd')
    infrastructure_state_cd = baseq.values_list('infrastructure_state_cd', flat=True).distinct().order_by('infrastructure_state_cd')
    project_activity_desc = baseq.values_list('project_activity_desc', flat=True).distinct().order_by('project_activity_desc')
    award_type = ['', 'Contract', 'Grant', 'Loan']
    pop_cong_dist = baseq.values_list('pop_cong_dist', flat=True).distinct().order_by('pop_cong_dist')

    filters = {'recipient_state': recipient_state,
               'awarding_agency_name': awarding_agency_name,
               'pop_state_cd': pop_state_cd,
               'infrastructure_state_cd': infrastructure_state_cd,
               'award_type': award_type,
               'project_activity_desc': project_activity_desc,
               'pop_cong_dist': pop_cong_dist, }

    cache.set(cache_key, filters, 60*60*24)

    return filters



@register.tag(name='isfilterselected')
def isfilterselected(parser, token):
    tokens = token.split_contents() 
    return IsSelectedNode(tokens[1])

class IsSelectedNode(template.Node):
    def __init__(self, fn):
        self.fn = fn
    def render(self, context):
        whichattr = context[self.fn]
        #options = context['filters'][whichattr]
        options = filters()[whichattr]
        try:
            selected = context['selectedfilters'][whichattr]
        except:
            selected = ''    
    
        ttlist = ['']
        for o in options:
            if o!='':
                if o==selected:
                    ttlist.append({'name': o,'selected': True})
                else:
                    ttlist.append({'name': o,'selected': False})
        context['ttlist'] = ttlist
        return '' 



@register.tag(name='getxylist')
def getxylist(parser, token):
    tokens = token.split_contents() 
    return getxyNode(tokens[0])

class getxyNode(template.Node):
    def __init__(self, fn):
        self.fn = fn
    def render(self, context):
        xy = context['xy']
        xychoices = context['xychoices']       
        xylist = []
        for x in xy:
            xylist.append({'id': xychoices.index(x),'name': x})
        context['orderedxy'] = xylist
        return '' 

     


@register.tag(name='getbykey')
def getbykey(parser, token):
    tokens = token.split_contents() 
    return getbykeyNode(tokens[1])

class getbykeyNode(template.Node):
    def __init__(self, fn):
        self.fn = fn
    def render(self, context):
        context['recsforkey'] =  Record.objects.filter(version_flag='F').exclude(status='x').filter(award_key=context[self.fn]['award_key']).order_by('recipient_role')
        return '' 


from django.template.defaultfilters import stringfilter
@register.filter(name='longtype')
@stringfilter
def longtype(s):
    types = {'L': 'Loan', 'C': 'Contract', 'G': 'Grant' }
    if s in types:
        return types[s]
    return s

from django.template.defaultfilters import stringfilter
@register.filter(name='cleankey')
@stringfilter
def cleankey(k):
    c = {'award_type':'Grant/Contract/Loan', 'awarding_agency_name': 'Awarding agency', 'project_activity_desc': 'Type of project', 'recipient_state': 'Recipient state', 'pop_state_cd': 'Place of performance', 'award_amount': 'Award amount', 'total_fed_arra_exp': 'Amount spent', 'number_of_jobs': 'Jobs funded 4th quarter', 'project_description': 'Project description', 'recipient_namee': 'Recipient', }
    if k in c:
        return c[k]
    else:
        return k

