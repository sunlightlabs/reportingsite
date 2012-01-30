from cStringIO import StringIO
from optparse import make_option
from zipfile import ZipFile
import csv
import datetime
import glob
import os
import pprint
import re
import sys
import tempfile
import time
import urllib2

from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.db.models import Q

from buckley.models import *

from get_ie_csvs import make_row_dict
from import_ies import committee_lookup, generic_querier, cursor
from elections import election_cycle



F5_FIELDS = [(0, 'form'),
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

SE_FIELDS = [(0, 'form'),
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

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--local',
            action='store',
            dest='local',
            default=False,
            help='Use local files rather than downloading from the FEC.'),
        )

    pp = pprint.PrettyPrinter(indent=4)

    def handle(self, *args, **options):

        for date in self.list_dates():
            print date

            datestr = date.strftime('%Y%m%d')

            if options.get('local'):
                iterator = glob.glob(os.path.join(options.get('local'), datestr) + '/*.fec')
                sleep = 0
            else:
                url = 'ftp://ftp.fec.gov/FEC/electronic/%s.zip' % datestr
                filename = self.dl_zipfile(url)
                if not filename:
                    continue
                iterator = self.decompress_zipfile(filename)
                sleep = 10

            for filepath in iterator:
                filing_number = os.path.split(filepath)[-1].replace('.fec', '')

                for row in self.parse_file_for_ies(filepath):
                    try:
                        row.update({'filing_number': filing_number, })
                        data = self.get_ie_data(row)
                        if data['expenditure_date'] < datetime.date(2010, 11, 3):
                            continue
                        self.save_ie(data)
                    except ValueError, e:
                        print >>sys.stderr, "Unparseable value in row: %s" % repr(row)
                        continue

            time.sleep(sleep)


    def save_ie(self, data):
        if not data['candidate_first'] and not data['candidate_last']:
            return

        data['cycle'] = election_cycle(data['expenditure_date']) # cycle is used by get_candidate
        data['payee'] = self.get_payee(data['payee_name'])
        data['committee'] = self.get_committee(data)
        data['candidate'] = self.get_candidate(data)
        if not data['candidate']:
            return

        if data['candidate'].cycle == 2010:
            data['candidate'] = deepcopy(data['candidate'])
            data['candidate'].cycle = 2012

        expenditure = self.create_expenditure(data)


    def create_expenditure(self, data):
        image_number = hash(str(data))
        try:
            return Expenditure.objects.get(image_number=image_number)
        except Expenditure.DoesNotExist:
            pass

        try:
            expenditure = Expenditure.objects.get(
                    image_number=image_number,
                    transaction_id=data['transaction_id'],
                    expenditure_date=data['expenditure_date'],
                    expenditure_amount=Decimal(data['expenditure_amount']),
                    expenditure_purpose=data['expenditure_purpose'],
                    candidate=data['candidate'],
                    committee=data['committee'])

        except Expenditure.DoesNotExist:
            # Need to figure out how to determine:
            #   - Election type
            #   - Amendment
            expenditure = Expenditure.objects.create(
                    image_number=hash(str(data)),
                    committee=data['committee'],
                    payee=data['payee'],
                    expenditure_purpose=data['expenditure_purpose'],
                    expenditure_amount=Decimal(data['expenditure_amount']),
                    support_oppose=data['support_oppose'],
                    election_type='', # How to determine this?
                    candidate=data['candidate'],
                    transaction_id=data['transaction_id'],
                    expenditure_date=data['expenditure_date'],
                    filing_number=data['filing_number'],
                    receipt_date=data['receipt_date'],
                    race=data['candidate'].race()
                    )


    def get_payee(self, name):
        slug = slugify(name)[:50]
        try:
            payee = Payee.objects.get(slug=slug)
        except Payee.DoesNotExist:
            payee = Payee.objects.create(
                    name=name,
                    slug=slug)
        return payee


    def get_candidate(self, data):
        data = self.handle_special_cases(data)

        if not data['candidate_id']:
            candidate = self.lookup_candidate_by_name(data)
            if not candidate:
                return None
            else:
                return candidate

        candidate = self.lookup_candidate_in_crp_table(data['candidate_id'])
        if candidate:
            try:
                try:
                    return Candidate.objects.get(crp_id=candidate['CID'])
                except Candidate.MultipleObjectsReturned:
                    try:
                        return Candidate.objects.get(crp_id=candidate['CID'],
                                                     office=data['candidate_office'])
                    except Candidate.MultipleObjectsReturned:
                        return Candidate.objects.get(crp_id=candidate['CID'],
                                                     office=data['candidate_office'],
                                                     cycle=data['cycle'])
            except Candidate.DoesNotExist:
                return self.create_candidate_from_crp(candidate, data)

        try:
            try:
                return Candidate.objects.get(fec_id=data['candidate_id'])
            except Candidate.MultipleObjectsReturned:
                return Candidate.objects.get(fec_id=data['candidate_id'],
                                             office=data['candidate_office'])
        except Candidate.DoesNotExist:
            return self.create_candidate_from_fec(data)

        print 'could not find/create:', data['candidate_id'], data['candidate_first'], data['candidate_last']


    def handle_special_cases(self, data):
        '''Handle special cases where we know the filter
        has filled out the form incorrectly.
        '''
        if data['candidate_last'] == 'Barak Obama':
            data.update({'candidate_first': 'Barack',
                         'candidate_last': 'Obama',
                         'candidate_id': 'P80003338', })

        elif data['candidate_first'] == 'Francisco Raul Quico':
            data.update({'candidate_id': 'H4TX28046', })

        elif data['candidate_first'] == 'Mike' and data['candidate_last'] == 'Pompeo':
            data.update({'candidate_id': 'H0KS04051', })

        return data


    def lookup_candidate_in_crp_table(self, fec_id):
        return generic_querier("SELECT * FROM candidates WHERE FECCandID = %s", [fec_id, ])


    def lookup_candidate_by_name(self, data):
        lf_fec_name = ('%(candidate_last)s, %(candidate_first)s %(candidate_middle)s' % data).strip()
        fl_fec_name = ('%(candidate_first)s %(candidate_last)s' % data).strip()
        try:
            return Candidate.objects.get(Q(fec_name=lf_fec_name) | Q(fec_name=fl_fec_name))
        except Candidate.DoesNotExist:
            pass

        # Fuzzy lookup of previously added candidates by first and last name
        candidates = Candidate.objects.filter(fec_name__icontains=data['candidate_first']) \
                                      .filter(fec_name__icontains=data['candidate_last'])
        if candidates:
            return candidates[0]
        else:
            # Fuzzy lookup of candidates in CRP database by first and last name.
            # If we find one, we can create a Candidate object.
            cursor.execute("""SELECT * FROM candidates
                                WHERE firstlastp LIKE %s
                                AND   firstlastp LIKE %s""", ['%%%(candidate_first)s%%' % data,
                                                              '%%%(candidate_last)s%%' % data, ])
            if cursor.rowcount:
                candidate = self.create_candidate_from_crp(dict(zip([x[0] for x in cursor.description], cursor.fetchone())), data)
            else:
                print 'not found:', data

            return None


    def create_candidate_from_fec(self, data):
        result = generic_querier("SELECT * FROM fec_candidate_master WHERE candidate_id = %s",
                                 [data['candidate_id'], ])
        if not result:
            return None

        candidate = Candidate.objects.create(
                        cycle=2012,
                        fec_id=result['candidate_id'],
                        fec_name=result['candidate_name'],
                        crp_id='',
                        crp_name='',
                        party=result['party'][0],
                        office=data['candidate_office'],
                        state=data['candidate_state'],
                        district=data.get('candidate_district'),
                        slug=slugify(result['candidate_name'])[:50]
                    )
        return candidate


    def create_candidate_from_crp(self, candidate, data):
        '''Creates a Candidate object based on data from
        CRP and the FEC.
        '''
        fec_name = generic_querier("SELECT candidate_name FROM fec_candidate_master WHERE candidate_id = %s",
                                    [candidate['FECCandID'], ])['candidate_name']
        crp_name = re.sub(r'\s\([A-Z0-9]\)', '', candidate.get('FirstLastP', ''))
        try:
            return Candidate.objects.get(crp_name=crp_name)
        except Candidate.DoesNotExist:
            pass

        party = re.search(r'\s\(([A-Z0-9])\)$', candidate.get('FirstLastP', ''))
        if party:
            party = party.groups()[0]
        else:
            party = ''

        candidate = Candidate.objects.create(
                        fec_id=candidate['FECCandID'],
                        fec_name=fec_name,
                        crp_id=candidate['CID'],
                        crp_name=crp_name,
                        party=party,
                        office=data['candidate_office'],
                        state=data['candidate_state'],
                        district=data['candidate_district'],
                        slug=slugify(crp_name)[:50]
                )
        return candidate


    def dl_zipfile(self, url):
        print url
        tf = tempfile.NamedTemporaryFile(mode='wb', delete=False)
        try:
            res = urllib2.urlopen(url)
        except urllib2.URLError:
            return None
        tf.write(res.read())
        return tf.name


    def decompress_zipfile(self, filename):
        zf = ZipFile(filename)
        for fn in zf.namelist():
            zf.extract(fn, path=tempfile.tempdir)
            yield os.path.join(tempfile.tempdir, fn)


    def get_ie_data(self, row):
        row['expenditure_date'] = dateparse(row['expenditure_date']).date()
        if row.has_key('receipt_date'):
            row['receipt_date'] = dateparse(row['receipt_date']).date()
        else:
            row['receipt_date'] = None

        row['committee'] = self.get_committee(row)
        return row


    def get_committee(self, row):
        try:
            committee_id = CommitteeId.objects.get(fec_committee_id=row['committee_id'])
            return committee_id.committee
        except CommitteeId.DoesNotExist:
            committee_dict = committee_lookup(row['committee_id'])
            if committee_dict:
                committee = self.create_committee(cid=row['committee_id'],
                                                  name=committee_dict['PACShort'])
                return committee

        committee = self.fec_committee_lookup(row['committee_id'])
        if committee:
            committee = self.create_committee(cid=row['committee_id'],
                                              name=committee)
            return committee

        #print 'not found:', row['committee_name'], row['committee_id']


    def create_committee(self, cid, name):
        committee, created = Committee.objects.get_or_create(
                name=self.committee_title_case(name),
                slug=slugify(name)[:50])
        committee_id = CommitteeId.objects.create(
                fec_committee_id=cid,
                committee=committee)
        return committee


    def committee_title_case(self, name):
        reserved = ['PAC', 'IE', ]

        p = re.compile(r'\b(%s)\b' % '|'.join(reserved), re.I)

        def repl(match):
            return match.group().upper()

        return p.sub(repl, name.title())


    def fec_committee_lookup(self, committee_id):
        query = "SELECT * FROM fec_committee_master WHERE committee_id = %s"
        params = [committee_id, ]
        return generic_querier(query, params).get('committee_name', '').strip()

    def get_cycle(self, date):
        if date < datetime.date(2011, 1, 1):
            return '2010'
        return '2012'

    def parse_file_for_ies(self, filepath):
        committee_name = None

        for line in open(filepath).readlines():
            line = line.strip().split('\x1c')

            form = line[0]

            if re.match(r'F(5N|24)', form):
                committee_name = line[3] # Save the committee name in case it's not in our database.
                continue

            elif re.search(r'^SE', form):
                try:
                    row = make_row_dict(line, SE_FIELDS)
                except IndexError:
                    print 'error:', filepath
                    continue

            elif re.match(r'F5(7|5)', form):
                if line[-2] == 'S': # Senate candidates might not have a district listed.
                    fields = F5_FIELDS[:-1]
                else:
                    fields = F5_FIELDS
            
                max_ix = max(map(lambda fs: fs[0], F5_FIELDS))
                if len(line) <= max_ix:
                    print >>sys.stderr, "`line` contains %d fields while F5_FIELDS requires %d" % (len(line), max_ix)
                    continue

                row = make_row_dict(line, fields)

            else:
                continue

            row['committee_name'] = committee_name
            yield row


    def output_data(self, line):
        csv.writer(sys.stdout).writerow(line)


    def list_dates(self):
        start = (datetime.date.today() - datetime.timedelta(days=7))
        end = datetime.date.today()
        curr = start
        while curr < end:
            yield curr
            curr += datetime.timedelta(days=1)
