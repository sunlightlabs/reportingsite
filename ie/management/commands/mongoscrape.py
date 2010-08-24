from cStringIO import StringIO
import csv
import datetime
import re
import sys
import time
import urllib

import httplib2
from pymongo import Connection
import MySQLdb
from django.template.defaultfilters import slugify

from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):

    help = "Scrape independent-expenditure data from the FEC"
    requires_model_validation = False

    def handle_noargs(self, **options):
        scraper = Scraper()
        scraper.clear_datastore()
        scraper.scrape()


def fixdate(date):
    """20100814
    MongoDB requires a datetime.datetime object (datetime.date won't work)
    """
    m = re.match(r'(?P<year>\d{4})(?P<month>\d\d)(?P<day>\d\d)', date)
    if m:
        return datetime.datetime(year=int(m.groupdict()['year']),
                                 month=int(m.groupdict()['month']),
                                 day=int(m.groupdict()['day'])
                                 )
    return None


def datechunk(start, end, days):
    curr = start
    while True:
        if curr+datetime.timedelta(days) > end:
            yield (curr, end)
            break
        yield (curr, curr+datetime.timedelta(days))
        curr = curr + datetime.timedelta(days+1)


def get_crp_data(fec_id):
    cursor = MySQLdb.Connection('localhost', 'campfin', 'campfin', 'campfin').cursor()
    query = "SELECT CID, FirstLastP FROM candidates WHERE feccandid = %s"
    cursor.execute(query, [fec_id, ])
    if cursor.rowcount:
        return cursor.fetchone()
    return ('', '')


#START = datetime.date.today() - datetime.timedelta(days=7)
START = datetime.date(2009, 01, 01)
END = datetime.date.today()

class Scraper(object):

    base_url = 'http://query.nictusa.com'
    headers = {
               # Form
               # FORM 24 - 24 OR 48 HOUR NOTICE OF INDEPENDENT EXPENDITURE
               'F24': ['FORM TYPE',
                       'FILER FEC ID NUMBER',
                       'REPORT TYPE',
                       'ORGANIZATION NAME',
                       'STREET 1',
                       'STREET 2',
                       'CITY',
                       'STATE',
                       'ZIP',
                       'TREASURER LAST NAME',
                       'TREASURER FIRST NAME',
                       'TREASURER MIDDLE NAME',
                       'TREASURER PREFIX',
                       'TREASURER SUFFIX',
                       'DATE SIGNED', ],
               # FORM 5 - REPORT OF INDEPENDENT EXPENDITURES MADE AND CONTRIBUTIONS RECEIVED 
               # F5N means Form 5 New which is what individuals or groups (corporations, unions?) 
               # who are not PACs or Parties use to submit their 24 and 48 hour notices
               'F5N': ['FORM TYPE',
                       'FILER FEC ID NUMBER',
                       'ENTITY TYPE',
                       'ORGANIZATION NAME',
                       'INDIVIDUAL LAST NAME',
                       'INDIVIDUAL FIRST NAME',
                       'INDIVIDUAL MIDDLE NAME',
                       'INDIVIDUAL PREFIX',
                       'INDIVIDUAL SUFFIX',
                       'CHANGE OF ADDRESS',
                       'STREET 1',
                       'STREET 2',
                       'CITY',
                       'STATE',
                       'ZIP',
                       'YES/NO (Qualified Non-Profit Corporation)',
                       'INDIVIDUAL EMPLOYER',
                       'INDIVIDUAL OCCUPATION',
                       'REPORT CODE',
                       'REPORT TYPE',
                       'COVERAGE FROM DATE',
                       'COVERAGE THROUGH DATE',
                       'TOTAL CONTRIBUTION',
                       'TOTAL INDEPENDENT EXPENDITURE',
                       'PERSON COMPLETING LAST NAME',
                       'PERSON COMPLETING FIRST NAME',
                       'PERSON COMPLETING MIDDLE NAME',
                       'PERSON COMPLETING PREFIX',
                       'PERSON COMPLETING SUFFIX',
                       'DATE SIGNED', ],
               # Contribution
               # FORM 5.6 - FOR EACH CONTRIBUTOR
               'F56': ['FORM TYPE',
                       'FILER COMMITTEE ID NUMBER',
                       'TRANSACTION ID NUMBER',
                       'ENTITY TYPE',
                       'CONTRIBUTOR ORGANIZATION NAME',
                       'CONTRIBUTOR LAST NAME',
                       'CONTRIBUTOR FIRST NAME',
                       'CONTRIBUTOR MIDDLE NAME',
                       'CONTRIBUTOR PREFIX',
                       'CONTRIBUTOR SUFFIX',
                       'CONTRIBUTOR STREET 1',
                       'CONTRIBUTOR STREET 2',
                       'CONTRIBUTOR CITY',
                       'CONTRIBUTOR STATE',
                       'CONTRIBUTOR ZIP',
                       'CONTRIBUTOR COMMITTEE FEC ID',
                       'CONTRIBUTION DATE',
                       'CONTRIBUTION AMOUNT',
                       'CONTRIBUTOR EMPLOYER',
                       'CONTRIBUTOR OCCUPATION', ],
               # Expenditure
               # FORM 5.7 - FOR EACH INDEPENDENT EXPENDITURE MADE
               'F57': ['FORM TYPE',
                       'FILER COMMITTEE ID NUMBER',
                       'TRANSACTION ID NUMBER',
                       'ENTITY TYPE',
                       'PAYEE ORGANIZATION NAME',
                       'PAYEE LAST NAME',
                       'PAYEE FIRST NAME',
                       'PAYEE MIDDLE NAME',
                       'PAYEE PREFIX',
                       'PAYEE SUFFIX',
                       'PAYEE STREET 1',
                       'PAYEE STREET 2',
                       'PAYEE CITY',
                       'PAYEE STATE',
                       'PAYEE ZIP',
                       'ELECTION CODE',
                       'ELECTION OTHER DESCRIPTION',
                       'EXPENDITURE DATE',
                       'EXPENDITURE AMOUNT',
                       'CALENDAR Y-T-D (per election/office)',
                       'EXPENDITURE PURPOSE CODE',
                       'EXPENDITURE PURPOSE DESCRIP',
                       'CATEGORY CODE',
                       'PAYEE CMTTE FEC ID NUMBER',
                       'SUPPORT/OPPOSE CODE',
                       'CANDIDATE ID NUMBER',
                       'CANDIDATE LAST NAME',
                       'CANDIDATE FIRST NAME',
                       'CANDINATE MIDDLE NAME',
                       'CANDIDATE PREFIX',
                       'CANDIDATE SUFFIX',
                       'CANDIDATE OFFICE',
                       'CANDIDATE STATE',
                       'CANDIDATE DISTRICT', ],
                # Expenditure
                # SCHEDULE E - ITEMIZED INDEPENDENT EXPENDITURES
                # SE is the code for Schedule E - that's what committees (PACs, Parties) 
                # use to submit their 24 and 48 hour notices
                'SE': ['FORM TYPE',
                       'FILER COMMITTEE ID NUMBER',
                       'TRANSACTION ID NUMBER',
                       'BACK REFERENCE TRAN ID NUMBER',
                       'BACK REFERENCE SCHED NAME',
                       'ENTITY TYPE',
                       'PAYEE ORGANIZATION NAME',
                       'PAYEE LAST NAME',
                       'PAYEE FIRST NAME',
                       'PAYEE MIDDLE NAME',
                       'PAYEE PREFIX',
                       'PAYEE SUFFIX',
                       'PAYEE STREET 1',
                       'PAYEE STREET 2',
                       'PAYEE CITY',
                       'PAYEE STATE',
                       'PAYEE ZIP',
                       'ELECTION CODE',
                       'ELECTION OTHER DESCRIPTION',
                       'EXPENDITURE DATE',
                       'EXPENDITURE AMOUNT',
                       'CALENDAR Y-T-D (per election/office)',
                       'EXPENDITURE PURPOSE CODE',
                       'EXPENDITURE PURPOSE DESCRIP',
                       'CATEGORY CODE',
                       'PAYEE CMTTE FEC ID NUMBER',
                       'SUPPORT/OPPOSE CODE',
                       'CANDIDATE ID NUMBER',
                       'CANDIDATE LAST NAME',
                       'CANDIDATE FIRST NAME',
                       'CANDINATE MIDDLE NAME',
                       'CANDIDATE PREFIX',
                       'CANDIDATE SUFFIX',
                       'CANDIDATE OFFICE',
                       'CANDIDATE STATE',
                       'CANDIDATE DISTRICT',
                       'COMPLETING LAST NAME',
                       'COMPLETING FIRST NAME',
                       'COMPLETING MIDDLE NAME',
                       'COMPLETING PREFIX',
                       'COMPLETING SUFFIX',
                       'DATE SIGNED',
                       'MEMO CODE',
                       'MEMO TEXT/DESCRIPTION', ],
              'TEXT': ['REC TYPE',
                       'FILER COMMITTEE ID NUMBER',
                       'TRANSACTION ID NUMBER',
                       'BACK REFERENCE TRAN ID NUMBER',
                       'BACK REFERENCE SCHED / FORM NAME',
                       'TEXT4000', ],
            }
    headers['F5A'] = headers['F57']

    date_fields = ['DATE SIGNED',
                   'COVERAGE FROM DATE',
                   'COVERAGE THROUGH DATE',
                   'CONTRIBUTION DATE',
                   'EXPENDITURE DATE', ]
    float_fields = ['EXPENDITURE AMOUNT',
                    'CONTRIBUTION AMOUNT', ]

    id_fields = ['CANDIDATE ID NUMBER',
                 'FILER COMMITTEE ID NUMBER', ]


    def __init__(self):
        self.db = Connection().independent_expenditures
        self.filers = self.db.filers
        self.contributions = self.db.contributions
        self.expenditures = self.db.expenditures
        self.text = self.db.text

        self.collections = {
                'F5N': self.filers,
                'F5A': self.filers,
                'F24': self.filers,
                'F56': self.contributions,
                'F57': self.expenditures,
                'SE': self.expenditures,
                'TEXT': self.text,
            }

        self.filers.ensure_index([('filing_id', 1), ], unique=True)
        self.contributions.ensure_index([('TRANSACTION ID NUMBER', 1), ], unique=True)
        self.expenditures.ensure_index([('TRANSACTION ID NUMBER', 1), ], unique=True)
        self.text.ensure_index([('filing_id', 1), ], unique=True)

        self.h = httplib2.Http('.cache')

    def clear_datastore(self):
        collections = [self.filers,
                       self.contributions,
                       self.expenditures,
                       self.text, ]
        for collection in collections:
            for entry in collection.find():
                collection.remove(entry['_id'])


    def scrape(self, start=START, end=END):

        url = 'http://query.nictusa.com/cgi-bin/dcdev/indexp/'

        for start_date, end_date in datechunk(start, end, 60):
            print start_date, end_date

            body = urllib.urlencode({'FROM': start_date.strftime('%m/%d/%Y'),
                                     'TO': end_date.strftime('%m/%d/%Y'), })
            response, content = self.h.request(url, method='POST', body=body)

            # We reverse the list so we get the oldest ones first,
            # and any amendments replace the original entries.
            download_lines = re.findall(r'.*\/cgi-bin\/dcdev\/forms\/DL\/\d+\/.*', content)
            download_lines.reverse()

            for line in download_lines:
                self.parse_download_page(line)

    def parse_download_page(self, line):
        if line.find('QUARTERLY') > 0 or line.find('YEAR-END') > 0:
            return

        link = re.search(r'\/cgi-bin\/dcdev\/forms\/DL\/\d+\/', line).group()

        url = '%s%s' % (self.base_url, link)

        filing_id = re.search(r'(\d+)\/$', url)
        if filing_id:
            filing_id = filing_id.groups()[0]
        else:
            filing = None

        response, content = self.h.request(url)

        match = re.search(r"(\/showcsv.*?)'", content)
        if not match:
            return

        csv_url = '%s%s' % (self.base_url, match.groups()[0])
        response, content = self.h.request(csv_url)
        print csv_url

        rows = list(csv.reader(StringIO(content)))
        for row in rows:
            if not row[0] or row[0] == 'HDR':
                continue

            data = dict(zip(self.headers[row[0]], row))
            data['filing_id'] = filing_id

            collection = self.collections[row[0]]

            # We need to clean up some fields for consistency
            # and to avoid duplicates.

            # Remove any previous entries with the
            # same transaction id number. This is a
            # unique field, but new entries won't override
            # old ones; we have to remove the old ones.
            if data.has_key('TRANSACTION ID NUMBER'):
                entry = collection.find_one({'TRANSACTION ID NUMBER': data['TRANSACTION ID NUMBER']})
                if entry:
                    collection.remove(entry['_id'])

            # Convert date strings to datetime objects.
            for field in self.date_fields:
                if data.has_key(field):
                    data[field] = fixdate(data[field])

            # Check whether this record is too old
            skip = False
            for field in ['CONTRIBUTION DATE', 'EXPENDITURE DATE', ]:
                if data.has_key(field):
                    if not data[field]:
                        skip = True
                        break
                    if data[field] < datetime.datetime(2009, 01, 01):
                        skip = True
                        break

            if skip:
                continue

            # Check whether a candidate ID exists
            if 'CANDIDATE ID NUMBER' in data:
                if not data['CANDIDATE ID NUMBER'].strip():
                    continue

            # Convert amount strings to floats.
            for field in self.float_fields:
                if data.has_key(field):
                    try:
                        data[field] = float(data[field])
                    except ValueError:
                        data[field] = 0

            # Ensure that all ID fields are uppercase,
            # so we can get accurate aggregate numbers.
            for field in self.id_fields:
                if data.has_key(field):
                    data[field] = data[field].upper()

            # Get CRP name and ID
            if data.has_key('CANDIDATE ID NUMBER'):
                if data['CANDIDATE ID NUMBER']:
                    data['crp_id'], data['crp_name'] = get_crp_data(data['CANDIDATE ID NUMBER'])
                    data['candidate_slug'] = slugify(re.sub(r' \([A-Z0-9]\)$', '', data['crp_name']))

            # Slugify the payee name
            if data.has_key('PAYEE ORGANIZATION NAME'):
                if data['PAYEE ORGANIZATION NAME']:
                    payee_name = data['PAYEE ORGANIZATION NAME']
                else:
                    payee_name = '%s, %s %s %s' % (data['PAYEE LAST NAME'],
                                                   data['PAYEE FIRST NAME'],
                                                   data['PAYEE MIDDLE NAME'],
                                                   data['PAYEE SUFFIX'])
                data['payee_name'] = payee_name
                data['payee_slug'] = slugify(payee_name)

            # Slugify the committee name
            if data.has_key('ORGANIZATION NAME'):
                data['committee_slug'] = slugify(data['ORGANIZATION NAME'])

            collection.insert(data)
