"""Get donor information for committees.
"""
from cStringIO import StringIO
from decimal import Decimal
import csv
import datetime
import re
import socket
import time
import urllib2
from hashlib import md5

try:
    import json
except ImportError:
    import simplejson as json

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.db import IntegrityError

from dateutil.parser import parse as dateparse

from buckley.models import *

MIN_DATE = datetime.date(2010, 11, 10)

socket.setdefaulttimeout(100000)


def get_form_urls(cid, use_min_date=True):
    """Get the URLs for monthly and quarterly reports.
    """
    url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/%s/' % cid
    page = urllib2.urlopen(url).read()
    filings = re.findall("<A HREF='(\d+)\/'>Form F3X?N - (\d\d\/\d\d\/\d\d\d\d)", page)

    # Schedule A is itemized receipts
    url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/DL/%s/'

    for id, date_filed in filings:
        date = dateparse(date_filed).date()
        if date < MIN_DATE and use_min_date:
            continue

        print date

        dlpage = urllib2.urlopen(url % id).read()
        m = re.search(r'\/showcsv\/.*\.fec', dlpage)
        if not m or m is None:
            yield None
        try:
            yield 'http://query.nictusa.com%s' % m.group()
        except AttributeError:
            m = re.search(r'\/comma\/\d+.fec', dlpage)
            if m:
                yield 'http://query.nictusa.com%s' % m.group()
            else:
                print 'AttributeError: %s' % dlpage
                yield None



def parse_donor_page(page):
    rows = re.findall(r'<TR ALIGN=CENTER>\s+<TD ROWSPAN=3 ALIGN=LEFT>.*?<BR><\/B><\/TD><\/TR>', page, re.S)
    for row in rows:
        data = parse_donor_row(row)
        if data:
            yield data

def parse_donor_list(url):
    time.sleep(20)
    try:
        page = urllib2.urlopen(url).read() 
    except socket.timeout:
        print 'Skipping %s' % url
        yield None
    for row in parse_donor_page(page):
        row['url'] = url
        yield row

    # Get data for paginated results
    m = re.search('page 1 of (\d+)', page, re.I)
    if m:
        max_page = int(m.groups()[0])
        for i in range(2, max_page+1):
            time.sleep(20)
            page = urllib2.urlopen('/'.join([url, str(i)])).read()
            for row in parse_donor_page(page):
                row['url'] = url
                yield row

def parse_donor_row(row):
    cells = re.findall(r'<TD.*?>(.*?)<\/TD>', row, re.S)
    try:
        (name_address, employer, date, amount, occupation, 
                blank, aggregate, memo) = [x.strip() for x in cells[:-2]]
    except ValueError: # Too many values to unpack; if info is missing
        return None

    memo = re.sub(r'<\/?B>', '', memo).strip().replace('<BR>', '')
    occupation = occupation.replace('<BR>', '')
    employer = employer.replace('<BR>', '')
    date = dateparse(date)

    try:
        name, street, city_zip = [x.strip() for x in re.sub(r'<\/?B>', '', cells[0]).split('<BR>')]
    except ValueError: # Too many values to unpack; if info is missing
        return None

    # Separate street into street1 and street2
    street_pieces = [x.strip() for x in street.split('\n')]
    if len(street_pieces) > 1:
        street1, street2 = street_pieces
    else:
        street1 = street_pieces[0]
        street2 = ''

    # Separate city, state and zipcode
    try:
        city, zipcode = city_zip.split('  ')
    except ValueError:
        city = city_zip
        zipcode = ''

    city_pieces = city.split(',')
    state = city_pieces[-1].strip()
    city = ','.join(city_pieces[:-1]).strip()

    return {'name': name,
            'street1': street1,
            'street2': street2,
            'city': city,
            'zipcode': zipcode,
            'state': state,
            'date': date,
            'memo': memo,
            'aggregate': Decimal(aggregate),
            'amount': Decimal(amount),
            'occupation': occupation, 
            'employer': employer,
            }


def parse_donor_csv(url):
    reader = csv.reader(StringIO(urllib2.urlopen(url).read()))
    for row in reader:
        if not row[0].startswith('SA11'):
            continue

        yield row


def save_row(row):
    try:
        contribution = Contribution.objects.create(**row)
    except (IntegrityError, Warning):
        return
    return contribution


def save_contribution(row, committee, url, filing_number):
    if row[5] == 'ORG':
        name = row[6]
    elif row[5] == 'PAC':
        name = row[6]
    else:
        name=('%s, %s %s %s' % (row[7],
                               row[8],
                               row[9],
                               row[11])).replace('  ', ' ').strip()

    data_row_hash = md5(str(row)).hexdigest()
    previously_saved = Contribution.objects.filter(data_row_hash=data_row_hash)
    if previously_saved:
        return None

    try:
        contribution = Contribution.objects.create(
                committee=committee,
                filing_number=filing_number,
                transaction_id=row[2],
                name=name,
                contributor_type=row[5],
                date=dateparse(row[19]).date(),
                employer=row[24],
                occupation=row[25],
                street1=row[12],
                street2=row[13],
                city=row[14],
                state=row[15],
                zipcode=row[16],
                amount=row[20],
                aggregate=row[21] or 0,
                memo=row[23],
                url=url,
                data_row=str(row),
                data_row_hash=data_row_hash
                )
    except IntegrityError:
        return
    return contribution


class Command(BaseCommand):
    
    def handle(self, *args, **options):

        apikey = ''
        if args:
            date = dateparse(args[0]).date()
        else:
            date = datetime.date.today()

        dates = []                                                                                                    
        curr = datetime.date(2010, 11, 4)                                                                             
        while True:                                                                                                   
            dates.append(curr)                                                                                        
            if curr == datetime.date.today():                                                                         
                break                                                                                                 
            curr += datetime.timedelta(1) 

        committees = []

        ids = list(CommitteeId.objects.values_list('fec_committee_id', flat=True))
        ieonly_ids = list(IEOnlyCommittee.objects.values_list('id', flat=True))
        ids = ids + ieonly_ids

        for date in dates:
            print date
            url = 'http://api.nytimes.com/svc/elections/us/v3/finances/2010/filings/%s.json?api-key=%s' % (date.strftime('%Y/%m/%d'), apikey)
            #url = 'http://projects.nytimes.com/campfin/svc/elections/us/v3/finances/2010/filings/%s.json' % date.strftime('%Y/%m/%d')
    
            response = urllib2.urlopen(url).read()
            data = json.loads(response)
    
            for result in data['results']:
                cid = re.search(r'C\d{8}', result['fec_uri']).group()
                #if cid in ids and ('QUARTER' in result['report_title'] or 'MONTH' in result['report_title'] or 'PRE-GENERAL' in result['report_title']):
		if cid in ids and 'POST-GENERAL' in result['report_title']:
                    try:
                        committee_id = CommitteeId.objects.get(fec_committee_id=cid)
                        committee = committee_id.committee
                    except CommitteeId.DoesNotExist:
                        continue
                        #committee = IEOnlyCommittee.objects.get(id=cid)

                    filing_number = result['fec_uri'].strip('/').split('/')[-1]
                    print committee
                    committees.append((committee, filing_number))

        for committee, filing_number  in committees:
            print committee, filing_number
            filing_url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/DL/%s/' % filing_number
            dlpage = urllib2.urlopen(filing_url).read()
            m = re.search(r'\/showcsv\/.*\.fec', dlpage)
            if not m or m is None:
                continue
            try:
                csv_url = 'http://query.nictusa.com%s' % m.group()
            except AttributeError:
                m = re.search(r'\/comma\/\d+.fec', dlpage)
                if m:
                    csv_url = 'http://query.nictusa.com%s' % m.group()
                else:
                    print 'AttributeError: %s' % dlpage
                    continue

            for row in parse_donor_csv(csv_url):
                contribution = save_contribution(row, committee, csv_url, filing_number)
                print committee, csv_url, contribution

            """
            try:
                id_set = committee.committeeid_set.all()
            except AttributeError:
                try:
                    id_set = CommitteeId.objects.filter(fec_committee_id=committee.id)
                except CommitteeId.DoesNotExist:
                    continue

            for cid in id_set:
                filing_urls = get_form_urls(cid)
                for url in filing_urls:
                    if not url:
                        continue

                    filing_number = url.split('/')[-1].replace('.fec', '')

                    for row in parse_donor_csv(url):
                        contribution = save_contribution(row, committee, url, filing_number)
                        print committee, url, contribution

            """
