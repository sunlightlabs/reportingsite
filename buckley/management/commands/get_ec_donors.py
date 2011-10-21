"""Get donor information for committees filing ECs.
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

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.db import IntegrityError

from dateutil.parser import parse as dateparse

from buckley.models import *


MIN_DATE = datetime.date(2009, 1, 1)

socket.setdefaulttimeout(100000)


class Command(BaseCommand):

    def handle(self, *args, **options):
        ec_committee_ids = Expenditure.objects.order_by('committee').filter(electioneering_communication=True).values_list('committee', flat=True).distinct()
        ec_committees = Committee.objects.filter(id__in=ec_committee_ids)

        for committee in ec_committees:
            print committee
            for committee_id in committee.committeeid_set.all():
                filings_url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/%s/' % committee_id.fec_committee_id
                print filings_url
                filings_page = urllib2.urlopen(filings_url).read()

                filings = re.findall(r"<A HREF='(?P<filing_number>\d+)\/'>Form F.*?(?P<date>\d\d\/\d\d\/\d\d\d\d)", filings_page)
                for filing in filings:
                    filing_number, date = filing
                    print filing_number, date
                    date = dateparse(date).date()
                    if date < MIN_DATE:
                        print 'too old'
                        continue

                    dl_url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/DL/%s/' % filing_number
                    dl_page = urllib2.urlopen(dl_url).read()

                    csv_re = re.search(r'\/showcsv\/.*\.fec', dl_page)
                    if not csv_re:
                        print 'NO CSV FOUND'

                    try:
                        csv_url = 'http://query.nictusa.com%s' % csv_re.group()
                    except AttributeError:
                        continue
                    reader = csv.reader(StringIO(urllib2.urlopen(csv_url).read()))

                    for row in reader:
                        if not row or len(row) < 20:
                            continue
                        if row[0] in ('F92' or 'F56'):
                            data_row_hash = md5(str(row)).hexdigest()
                            previously_saved = Contribution.objects.filter(data_row_hash=data_row_hash)
                            if previously_saved:
                                print 'previously saved'
                                continue

                            transaction_id = row[2]
                            contributor_type = row[5]
                            if contributor_type == 'IND':
                                name=('%s, %s %s %s' % (row[7],
                                                        row[8],
                                                        row[9],
                                                        row[11])).replace('  ', ' ').strip()
                            else:
                                name = row[6]
                            date = dateparse(row[17]).date()
                            employer = ''
                            occupation = ''
                            street1 = row[12]
                            street2 = row[13]
                            city = row[14]
                            state = row[15]
                            zipcode = row[16]
                            amount = row[18]
                            aggregate = 0
                            memo = ''
                            url = csv_url
                            data_row = str(row)
                            data_row_hash=data_row_hash

                            try:
                                contribution = Contribution.objects.create(
                                        committee=committee,
                                        filing_number=filing_number,
                                        transaction_id=transaction_id,
                                        name=name,
                                        contributor_type=contributor_type,
                                        date=date,
                                        street1=street1,
                                        street2=street2,
                                        city=city,
                                        state=state,
                                        zipcode=zipcode,
                                        amount=amount,
                                        aggregate=0,
                                        url=csv_url,
                                        data_row=str(row),
                                        data_row_hash=data_row_hash
                                        )
                            except IntegrityError:
                                print 'integrity error'
                                continue
                            print contribution

