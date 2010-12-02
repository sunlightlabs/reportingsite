from django import template

register = template.Library()

@register.filter(name='percentage')
def percentage(value, arg):
    """Get the percentage of value in arg."""
    return int(round((float(value)/float(arg))*100))
