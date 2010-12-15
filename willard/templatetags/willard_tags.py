from django import template

from willard.models import *

register = template.Library()

@register.tag(name='registration_count')
def registration_count(parser, token):
    try:
        tag_name, date, period = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, '%r tag requires two arguments' % token.contents.split()[0]
    return RegistrationCountNode(date, period)


class RegistrationCountNode(template.Node):

    def __init__(self, date, period):
        self.date = template.Variable(date)
        self.period = period

    def render(self, context):
        date = self.date.resolve(context)
        if self.period == 'year':
            params = {'signed_date__year': date.year, }
        elif self.period == 'month':
            params = {'signed_date__year': date.year, 
                      'signed_date__month': date.month, }
        elif self.period == 'day':
            params = {'signed_date__year': date.year, 
                      'signed_date__month': date.month, 
                      'signed_date__day': date.day, }
        else:
            raise template.TemplateSyntaxError, 'period must by one of "year", "month", or "day"'

        return Registration.objects.filter(**params).count()
