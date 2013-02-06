from email.utils import formatdate
import datetime

from django import template

register = template.Library()


# util methods

def unix_time(dt):
	epoch = datetime.datetime.utcfromtimestamp(0)
	delta = dt - epoch
#	return delta.total_seconds()
## total_seconds() is python 2.7 forwards--instead use:
    return delta.days*86400+delta.seconds

def unix_time_millis(dt):
	return unix_time(dt) * 1000.0


# filters

@register.filter
def rfc822(dt):
	return formatdate(unix_time(dt))