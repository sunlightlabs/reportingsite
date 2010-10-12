"""To get independent expenditures more up-to-date, we can
get CSVs of each filing (http://query.nictusa.com/cgi-bin/dcdev/indexp/7)
(http://query.nictusa.com/cgi-bin/dcdev/indexp/1)
"""
from cStringIO import StringIO
import csv
import datetime
import re
import urllib2

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.template.defaultfilters import slugify

from dateutil.parser import parse as dateparse

from buckley.models import *
from import_ies import committee_lookup, candidate_lookup_by_id


def make_row_dict(row, fields):
    data = {}
    for index, field in fields:
        data[field] = row[index]
    return data


class Command(BaseCommand):

    def handle(self, *args, **options):
        url = 'http://query.nictusa.com/cgi-bin/dcdev/indexp/1'
        page = urllib2.urlopen(url).read()
        filings = re.findall(r'FEC-(\d+)', page)
        dl_url = 'http://query.nictusa.com/cgi-bin/dcdev/forms/DL/%s/'
        urls = [dl_url % x for x in filings]

        f5_fields = [(0, 'form'),
                     (1, 'committee_id'),
                     (2, 'transaction_id'),
                     (3, 'entity_type'),
                     (4, 'payee_name'),
                     (17, 'expenditure_date'),
                     (18, 'expenditure_amount'),
                     (21, 'expenditure_purpose'),
                     (24, 'support_oppose'),
                     (25, 'candidate_id'),
                     (26, 'candidate_last'),
                     (27, 'candidate_first'),
                     (28, 'candidate_middle'),
                     (31, 'candidate_office'),
                     (32, 'candidate_state'),
                     (33, 'candidate_district'), ]
        se_fields = [(0, 'form'),
                     (1, 'committee_id'),
                     (2, 'transaction_id'),
                     (5, 'entity_type'),
                     (6, 'payee_name'),
                     (19, 'expenditure_date'),
                     (20, 'expenditure_amount'),
                     (23, 'expenditure_purpose'),
                     (26, 'support_oppose'),
                     (27, 'candidate_id'),
                     (28, 'candidate_last'),
                     (29, 'candidate_first'),
                     (30, 'candidate_middle'),
                     (33, 'candidate_office'),
                     (34, 'candidate_state'),
                     (35, 'candidate_district'),
                     (41, 'receipt_date')]

        for url in urls:
            filing_number = url.strip('/').split('/')[-1]
            dlpage = urllib2.urlopen(url).read()
            m = re.search(r'\/showcsv\/.*\.fec', dlpage)
            if not m:
                continue
            csv_url = 'http://query.nictusa.com%s' % m.group()
            reader = csv.reader(StringIO(urllib2.urlopen(csv_url).read()))
            for row in reader:
                if row[0] == 'F57' or row[0] == 'F5N':
                    if len(row) < 33:
                        continue
                    row = make_row_dict(row, f5_fields)
                elif row[0] == 'SE':
                    row = make_row_dict(row, se_fields)
                elif row[0] == 'F24' or row[0] == 'F5A':
                    committee_name = row[3]
                    continue
                else:
                    continue

                row['expenditure_date'] = dateparse(row['expenditure_date'])
                if row.has_key('receipt_date'):
                    row['receipt_date'] = dateparse(row['receipt_date'])
                else:
                    row['receipt_date'] = datetime.date.today()

                try:
                    committee_id = CommitteeId.objects.get(fec_committee_id=row['committee_id'])
                    if committee_id:
                        committee = committee_id.committee
                except CommitteeId.DoesNotExist:
                    committee = committee_lookup(row['committee_id'])
                    row.update(committee)

                    if row.get('PACShort', '').strip():
                        committee_name = row['PACShort'].strip()
                    else:
                        committee_name = committee_name.strip().title()

                    committee, created = Committee.objects.get_or_create(
                            name=committee_name,
                            slug=slugify(committee_name)[:50]
                        )
                    committee_id = CommitteeId.objects.create(
                            fec_committee_id=row['committee_id'],
                            committee=committee)

                print committee

                try:
                    if row['candidate_id']:
                        candidate = Candidate.objects.get(fec_id=row['candidate_id'])
                    else:
                        raise Candidate.DoesNotExist
                except Candidate.DoesNotExist:
                    candidate = candidate_lookup_by_id(row['candidate_id'])
                    if not candidate:
                        try:
                            if row['candidate_first'] == 'MICHAEL' and row['candidate_last'] == 'FITZPATRICK (PA)':
                                candidate = Candidate.objects.get(slug='michael-g-fitzpatrick')
                            else:
                                candidate = Candidate.objects.get(slug=slugify(' '.join([row['candidate_first'], row['candidate_last']])))
                        except Candidate.DoesNotExist:
                            continue
                    else:
                        row.update(candidate)
                        crp_name = re.sub(r'\s\([A-Z0-9]\)', '', row.get('FirstLastP', ''))
                        try:
                            candidate = Candidate.objects.get(slug=slugify(crp_name)[:50])
                        except Candidate.DoesNotExist:

                            if crp_name:
                                party = re.search(r'\([A-Z0-9]\)$', row.get('FirstLastP', ''))
                                if party:
                                    try:
                                        party = party.groups()[0]
                                    except IndexError:
                                        party = ''
                                else:
                                    party = ''
                            else:
                                party = ''

                            fec_name = ('%(candidate_last)s, %(candidate_first)s %(candidate_middle)s' % row).strip()
                            if crp_name:
                                candidate_name = crp_name
                            else:
                                candidate_name = fec_name

                            candidate = Candidate.objects.create(
                                    fec_id=row['candidate_id'],
                                    fec_name=fec_name,
                                    crp_id=row.get('CID', ''),
                                    crp_name=crp_name,
                                    party=party,
                                    office=row['candidate_office'],
                                    state=row['candidate_state'],
                                    district=row['candidate_district'],
                                    slug=slugify(candidate_name)[:50]
                                    )

                try:
                    payee = Payee.objects.get(slug=slugify(row['payee_name'])[:50])
                except Payee.DoesNotExist:
                    payee = Payee.objects.create(
                            name=row['payee_name'],
                            slug=slugify(row['payee_name'])[:50])

                # These filings do not include the image number.
                # Need to keep this in mind when doing dupe-checking.
                image_number = 0

                try:
                    expenditure = Expenditure.objects.get(
                            transaction_id=row['transaction_id'],
                            expenditure_date=row['expenditure_date'],
                            expenditure_amount=Decimal(row['expenditure_amount']),
                            expenditure_purpose=row['expenditure_purpose'],
                            candidate=candidate,
                            committee=committee)
                    print 'Found %s' % expenditure
                except Expenditure.DoesNotExist:

                    try:
                        expenditure = Expenditure.objects.create(
                                image_number=hash(str(row)), # made up
                                committee=committee,
                                payee=payee,
                                expenditure_purpose=row['expenditure_purpose'],
                                expenditure_date=row['expenditure_date'],
                                expenditure_amount=Decimal(row['expenditure_amount']),
                                support_oppose=row['support_oppose'],
                                election_type='G', # Only using this script on new filings; all G
                                candidate=candidate,
                                transaction_id=row['transaction_id'],
                                filing_number=filing_number,
                                receipt_date=row['receipt_date'],
                                race=candidate.race()
                                )
                    except IntegrityError:
                        continue

                print expenditure.id

        # Get rid of duplicate candidate slugs
        noparty = Candidate.objects.filter(party='')
        for bad in noparty:
            good = Candidate.objects.filter(slug=candidate.slug).exclude(party='')
            if good:
                good = good[0]
                bad.expenditure_set.update(candidate=good)
                bad.delete()

        # Remove errors
        bad = []
        for expenditure in Expenditure.objects.filter(electioneering_communication=False):
            if expenditure.race != expenditure.candidate.race():
                bad.append(expenditure)
        for b in bad:
            b.delete()

        # denormalize
        for candidate in Candidate.objects.all():
            candidate.denormalize()


        cache.delete('buckley:widget2')
