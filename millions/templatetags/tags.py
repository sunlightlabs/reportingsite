from django import template
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


"""    filters = {'recipient_statee': recipient_statee, 'awarding_agency_name': awarding_agency_name, 'pop_state_cd': pop_state_cd, 'infrastructure_state_cd': infrastructure_state_cd }
    filterparams = ['awarding_agency_name', 'infrastructure_state_cd']"""

     


