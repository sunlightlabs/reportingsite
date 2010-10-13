"""Get donor information for committees.
"""
from decimal import Decimal
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

socket.setdefaulttimeout(25)


def get_form_urls(cid):
    """Get the URLs for monthly and quarterly reports.
    """
    url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/%s/' % cid
    page = urllib2.urlopen(url).read()
    filings = re.findall("<A HREF='(\d+)\/'>Form F3X?N - (\d\d\/\d\d\/\d\d\d\d)", page)

    # Schedule A is itemized receipts
    url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%%s/sa/ALL' % cid

    for id, date_filed in filings:
        date = dateparse(date_filed).date()
        if date < MIN_DATE:
            continue
        yield url % id


def parse_donor_page(page):
    rows = re.findall(r'<TR ALIGN=CENTER>\s+<TD ROWSPAN=3 ALIGN=LEFT>.*?<BR><\/B><\/TD><\/TR>', page, re.S)
    for row in rows:
        data = parse_donor_row(row)
        if data:
            yield data

def parse_donor_list(url):
    time.sleep(5)
    page = urllib2.urlopen(url).read()
    for row in parse_donor_page(page):
        row['url'] = url
        yield row

    # Get data for paginated results
    m = re.search('page 1 of (\d+)', page, re.I)
    if m:
        max_page = int(m.groups()[0])
        for i in range(2, max_page+1):
            time.sleep(5)
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


def save_row(row):
    try:
        contribution = Contribution.objects.create(**row)
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

        committees = Committee.objects.all()
        for committee in committees:

            #if not committee.ieonly_url():
            #    continue

            for cid in committee.committeeid_set.all():
                filing_urls = get_form_urls(cid)
                for url in filing_urls:
                    if url in already:
                        continue

                    #print url
                    filing_number = url.split('/')[-3]
                    for row in parse_donor_list(url):

                        row['committee'] = committee
                        row['filing_number'] = filing_number

                        print row
                        contribution = save_row(row)

