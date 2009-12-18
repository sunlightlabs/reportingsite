from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

BR_RE = re.compile(r'<br(.*?)>', re.I)
P_RE = re.compile(r'</?p>', re.I)
SPAN_RE = re.compile(r'</?span(.*?)>')

@register.filter
@stringfilter
def cleantags(value):
    value = BR_RE.sub('\n', value)
    value = P_RE.sub('\n', value)
    value = SPAN_RE.sub('', value)
    return value
