from django import template
from reportingsite.millions.models import *

register = template.Library()

@register.tag(name='isfilterselected')
def isfilterselected(parser, token):
    tokens = token.split_contents() 
    return IsSelectedNode(tokens[1])

class IsSelectedNode(template.Node):
    def __init__(self, fn):
        self.fn = fn
    def render(self, context):
        whichattr = context[self.fn]
        options = context['filters'][whichattr]
        selected = context['selectedfilters'][whichattr]
        
        ttlist = []
        for o in options:
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
@register.filter(name='cleankey')
@stringfilter
def cleankey(k):
    c = {'award_type':'Award type', 'awarding_agency_name': 'Awarding agency', 'project_activity_desc': 'Description of project', 'recipient_state': 'Recipient state', 'pop_state_cd': 'Place of performance', 'award_amount': 'Award Amount', 'total_fed_arra_exp': 'Amount Spent', 'number_of_jobs': 'Jobs Created 4th quarter', 'project_description': 'Project description', 'recipient_namee': 'Recipient'}
    if k in c:
        return c[k]
    else:
        return k

