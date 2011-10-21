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
        'Registration Statement': 'The registration statement is the first filing for the person or orgnization who lobbies on behalf of a foreign entity.',
        'Supplemental Statement': 'The supplemental statement provides information on what kind of public relations and lobbying a firm engages in on behalf of a foreign government.',
        'Amendment': 'An amendment makes corrections to past filings.',
        'Short-Form': 'Every six months, the short form is filed by each person involved in representing a foreign agent.',
        'Exhibit A': 'Exhibit A is filed for each foreign principle and gives an overview of the foreign organization.',
        'Exhibit AB': 'Exhibit B is the agreement between the foreign organization and the firm or person the organization hires. This usually contains a copy of the contract they sign.',
        'Exhibit B': 'Exhibit B is the agreement between the foreign organization and the firm or person the organization hires. This usually contains a copy of the contract they sign.',
        'Exhibit C': 'Exhibit C contains the articles of incorporation, bylaws and other documents that pertain to the registrant, the person or company that represents the foreign agent.',
        'Exhibit D': 'Exhibit D outlines fundraising information on behalf of the foreign agent.',
        'Conflict Provision': 'Conflict Provision a letter that is filed to allow a public official to represent a foreign entity. The employer must certify this position is to promote the national interest.',
    }
    return definitions.get(value, '')
