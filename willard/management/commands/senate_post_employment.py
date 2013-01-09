"""
http://www.senate.gov/legislative/termination_disclosure/2008/report2008.xml
http://www.senate.gov/legislative/termination_disclosure/2009/report2009.xml
"""
import socket
import urllib2
from dateutil.parser import parse as dateparse
import lxml.etree
import lxml.html

from django.db import IntegrityError
from willard.models import PostEmploymentNotice

socket.setdefaulttimeout(60*60*60)


def get_senate(year):
    if (year==2012):
        url = 'http://www.senate.gov/legislative/termination_disclosure/report2012.xml'
    if (year==2013):
        # they don't have this file made yet. 
        return None 
    else:
        url = 'http://senate.gov/legislative/termination_disclosure/%s/report%s.xml' % (year, year)

    print url
    doc = lxml.etree.fromstring(urllib2.urlopen(url).read())
    
    print "Got doc %s" % (doc)

    for employee in doc.xpath('previous_employee'):
        employee = lxml.etree.fromstring(lxml.etree.tostring(employee))
        data = {}
        for key in ['first', 'middle', 'last', 
                    'office_name', 'begin_date', 'end_date']:
            try:
                data[key] = employee.xpath('//%s' % key)[0].text
            except IndexError:
                data[key] = ''

        data['body'] = 'Senate'
        data['begin_date'] = dateparse(data['begin_date'])
        try:
            data['end_date'] = dateparse(data['end_date'])
        except ValueError:
            month, day, year = [int(x) for x in data['end_date'].split('/')]
            data['end_date'] = datetime.date(year, month, day-1)

        try:
            employee = PostEmploymentNotice.objects.create(**data)
            print "Added employee: %s" % (employee)
        except IntegrityError:
            pass

        


