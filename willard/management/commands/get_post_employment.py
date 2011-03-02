import datetime
from optparse import make_option
import re
import socket
import time
import urllib
import urllib2

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from willard.models import PostEmploymentNotice

from dateutil.parser import parse as dateparse
import lxml.etree
import lxml.html


socket.setdefaulttimeout(60*60*60)


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('--body',
                action='store',
                dest='body',
                default=None,
                help='The body for which to retrieve data',
            ),
    )

    def get_senate(self, year):
        if year == '2011':
            url = 'http://senate.gov/legislative/termination_disclosure/report2011.xml'
        else:
            url = 'http://senate.gov/legislative/termination_disclosure/%s/report%s.xml' % (year, year)

        print url
        doc = lxml.etree.fromstring(urllib2.urlopen(url).read())

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

            yield data


    def get_house(self):
        """The House search is broken. It ignores the year parameter.
        Therefore, to avoid timeouts because of too-big pages, we need
        to get the data by month.
        """
        base_url = 'http://clerk.house.gov/public_disc/employment.html'

        for month in range(1, 13):
            time.sleep(30)
            if month < 10:
                month = '0%s' % month
            body = {'action': 'sort',
                    'sortby': 'LastName',
                    'term_date0': '%s/01/2010' % month,
                    'term_date1': '%s/31/2010' % month,
                    }
            url = '%s?%s' % (base_url,
                             urllib.urlencode(body))

            page = urllib2.urlopen(url).read()
            doc = lxml.html.fromstring(page)
            table = doc.cssselect('#search_results')[0]
            for row in table.cssselect('tr')[1:]:
                name, office_name, begin_date, end_date = [x.text for x in row.getchildren()]

                try:
                    last, first = name.split(',')
                except ValueError:
                    last = name
                    first = ''

                office_name = re.sub(r' - \(\)', '', office_name)

                yield {'first': first.strip(),
                       'last': last.strip(),
                       'middle': '',
                       'office_name': office_name,
                       'begin_date': dateparse(begin_date),
                       'end_date': dateparse(end_date),
                       'body': 'House',
                        }


    def save_employee(self, employee):
        try:
            employee = PostEmploymentNotice.objects.create(**employee)
        except IntegrityError:
            pass

        print employee


    def handle(self, *args, **options):
        for employee in self.get_senate('2011'):
            print employee
            self.save_employee(employee)
        for employee in self.get_house():
            print employee
            self.save_employee(employee)
