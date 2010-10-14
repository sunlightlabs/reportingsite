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

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.db import IntegrityError

from dateutil.parser import parse as dateparse

from buckley.models import Committee, Contribution

MIN_DATE = datetime.date(2010, 9, 1)

socket.setdefaulttimeout(1000)


def get_form_urls(cid):
    """Get the URLs for monthly and quarterly reports.
    """
    url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/%s/' % cid
    page = urllib2.urlopen(url).read()
    filings = re.findall("<A HREF='(\d+)\/'>Form F3X?N - (\d\d\/\d\d\/\d\d\d\d)", page)

    # Schedule A is itemized receipts
    url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/DL/%s/'

    for id, date_filed in filings:
        date = dateparse(date_filed).date()
        if date < MIN_DATE:
            continue

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
    except IntegrityError:
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


    try:
        contribution = Contribution.objects.create(
                committee=committee,
                filing_number=filing_number,
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
                data_row=str(row)
                )
    except IntegrityError:
        return
    return contribution


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        already = list(Contribution.objects.order_by('url').values_list('url', flat=True).distinct())
        last_contributions = Contribution.objects.order_by('-pk')
        if last_contributions:
            last_contribution_url = last_contributions[0].url
            del already[already.index(last_contribution_url)]

        committees = Committee.objects.all().reverse()
        for committee in committees:

            #if not committee.ieonly_url():
            #    continue

            for cid in committee.committeeid_set.all():
                filing_urls = get_form_urls(cid)
                for url in filing_urls:
                    if not url:
                        continue

                    if url in already:
                        continue

                    filing_number = url.split('/')[-1].replace('.fec', '')

                    for row in parse_donor_csv(url):
                        contribution = save_contribution(row, committee, url, filing_number)
                        print committee, url, contribution


"""

                        print ' | '.join([str(len(row)), 
                                          row[0],
                                          row[1],
                                          row[2],
                                          row[4],
                                          row[5],
                                          row[6],
                                          row[7], #last
                                          row[8], #first
                                          row[9], #middle
                                          row[10], #prefix
                                          row[11], #suffix
                                          row[12], #street1
                                          row[13], #street2
                                          row[14], #city
                                          row[15], #state
                                          row[16], #zipcode
                                          row[17], #
                                          row[18], #
                                          row[19], #date
                                          row[20], #amt
                                          row[21], #aggregate
                                          row[22], #sometimes '15'
                                          row[23], #blank - memo?
                                          row[24], #employer
                                          row[25], #occupation
                                          row[26], #blank
                                          row[27],
                                          row[28],
                                          row[29],
                                          row[30],
                                          ])
['SA17', 'C00255752', 'SA17.89416', '', '', 'ORG', 'NORTHERN TRUST CO', '', '', '', '', '', '50 S LASALLE', '', 'CHICAGO', 'IL', '60675', '', '', '20100831', '28.34', '124.28', '', 'INTEREST INCOME', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
form_type,
committee_id,
entity_type,
contributor,
street1,
street2,
city,
state,
zipcode,
item_elect_cd,
item_elect_other,
indemp,
indocc,
aggregate,
date,
amount,
trans_code,
trans_description,
fec_committee_id,
fec_candidate_id,
candidate_name,
candidate_office,
candidate_state,
candidate_district,
conduit_name,
conduit_street1,
conduit_street2,
conduit_city,
conduit_state,
conduit_zip,
memo_code,
memo_text,
amended_cd,
tran_id,
back_ref_tran_id,

                    FORM TYPE
FILER FEC CMTE ID

ENTITY TYPE
CONTRIBUTOR NAME

STREET  1
STREET  2
CITY
STATE
ZIP

ITEM ELECT CD
ITEM ELECT OTHER

INDEMP
INDOCC

AGGREGATE AMT Y-T-D
DATE RECEIVED
AMOUNT RECEIVED

TRANS CODE
TRANS DESCRIP

FEC COMMITTEE ID NUMBER

FEC CANDIDATE ID NUMBER
CANDIDATE NAME
CAN/OFFICE
CAN/STATE 
CAN/DIST

CONDUIT NAME
CONDUIT STREET1
CONDUIT STREET2
CONDUIT CITY
CONDUIT STATE
CONDUIT ZIP

MEMO CODE
MEMO TEXT

AMENDED CD
TRAN ID

BACK REF TRAN ID
BACK REF SCHED NAME

Reference to SI or SL system code that identifies the Account

INCREASED LIMIT

CONTRIB ORGANIZATION NAME
CONTRIBUTOR LAST NAME
CONTRIBUTOR FIRST NAME
CONTRIBUTOR MIDDLE NAME
CONTRIBUTOR PREFIX
CONTRIBUTOR SUFFIX
                    for row in parse_donor_list(url):

                        if not row: 
                            continue

                        row['committee'] = committee
                        row['filing_number'] = filing_number

                        print row
                        contribution = save_row(row)
                    """
