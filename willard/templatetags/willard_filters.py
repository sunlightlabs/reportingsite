from django import template

register = template.Library()

@register.filter(name='percentage')
def percentage(value, arg):
    """Get the percentage of value in arg."""
    return int(round((float(value)/float(arg))*100))

@register.filter(name='form_definition')
def form_definition(value):
    """Return a description of the given type of form."""
    definitions = {
        'Registration Statement': 'Initial filing for primary registrant',
        'Supplemental Statement': '6 month activities and financial information',
        'Amendment': 'Corrections/additions to filings',
        'Short-Form': 'Individual foreign agents',
        'Exhibit A': 'Foreign principal',
        'Exhibit AB': 'Foreign principal agreement',
        'Exhibit B': 'Foreign principal agreement',
        'Exhibit C': 'Articles of incorporation, bylaws, etc.',
        'Exhibit D': 'Fundraising information',
        'Conflict Provision': 'Related Statute; 18 U.S.C. 219',
    }
    return definitions.get(value, '')
