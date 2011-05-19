"""To get independent expenditures more up-to-date, we can
get CSVs of each filing (http://query.nictusa.com/cgi-bin/dcdev/indexp/7)
(http://query.nictusa.com/cgi-bin/dcdev/indexp/1)
"""
from cStringIO import StringIO
import csv
import datetime
import re
import urllib2
import socket

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.db.models import *
from django.template.defaultfilters import slugify

from dateutil.parser import parse as dateparse

from buckley.models import *
from buckley.management.commands.cache_totals import cache_totals
from get_donors import get_form_urls, parse_donor_csv, save_contribution
from import_ies import committee_lookup, candidate_lookup_by_id


def make_row_dict(row, fields):
    data = {}
    for index, field in fields:
        data[field] = row[index]
    return data


socket.setdefaulttimeout(1000)


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
                amendment = 'N'
                if row[0] == 'F57' or row[0] == 'F5A':
                    if len(row) < 33:
                        continue
                    if row[0] == 'F5A':
                        amendment = 'A1'
                    row = make_row_dict(row, f5_fields)
                elif row[0] == 'SE':
                    row = make_row_dict(row, se_fields)
                elif row[0] == 'F24' or row[0] == 'F5N':
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
                    else:
                        continue
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

                    print created
                    if created: # Get committee's previous contributions
                        print row['committee_id']
                        for csv_url in get_form_urls(row['committee_id']):
                            if not csv:
                                continue
                            print 'Getting contributions'
                            filing_number = csv_url.split('/')[-1].replace('.fec', '')
                            print filing_number
                            for csv_row in parse_donor_csv(csv_url):
                                contribution = save_contribution(csv_row, committee, csv_url, filing_number)
                                print contribution

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
                            candidate = get_candidate(row)
                            #print candidate
                            #print 'Candidate.DoesNotExist'
                            #continue
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
                                    cycle=2012,
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

                except Expenditure.MultipleObjectsReturned:
                    continue

                except Expenditure.DoesNotExist:
                    special_elections = (('NY', 26, ),
                                         ('CA', 36, ), )
                    special = (candidate.state in [x[0] for x in special_elections] 
                                and
                               candidate.district in [x[1] for x in special_elections])
                    election_type = ('O' if special else 'P')

                    if row['expenditure_date'].year >= 2011:
                        cycle = '2012'
                    else:
                        cycle = '2010'
                    if candidate.cycle != cycle:
                        candidate = deepcopy(candidate)
                        candidate.id = None
                        candidate.cycle = cycle
                        candidate.save()

                    try:
                        expenditure = Expenditure.objects.create(
                                image_number=hash(str(row)), # made up
                                committee=committee,
                                payee=payee,
                                expenditure_purpose=row['expenditure_purpose'],
                                expenditure_date=row['expenditure_date'],
                                expenditure_amount=Decimal(row['expenditure_amount']),
                                support_oppose=row['support_oppose'],
                                election_type=election_type, # Only using this script on new filings; all G
                                candidate=candidate,
                                transaction_id=row['transaction_id'],
                                filing_number=filing_number,
                                receipt_date=row['receipt_date'],
                                race=candidate.race(),
                                amendment=amendment
                                )
                    except IntegrityError:
                        continue

                print expenditure.id

        return
        # Get rid of duplicate candidate slugs
        print 'removing duplicate candidate slugs'
        noparty = Candidate.objects.filter(party='')
        for bad in noparty:
            good = Candidate.objects.filter(slug=bad.slug).exclude(party='')
            if good:
                good = good[0]
                bad.expenditure_set.update(candidate=good)
                bad.delete()

        # Remove errors
        print 'removing errors where expenditure race != candidate race'
        bad = []
        for expenditure in Expenditure.objects.filter(electioneering_communication=False):
            if expenditure.race != expenditure.candidate.race():
                bad.append(expenditure)
        for b in bad:
            b.delete()

        try:
            bad = Committee.objects.get(name='New Prosperity Foundation, The')
            good = Committee.objects.get(name='The New Prosperity Foundation')
            bad.expenditure_set.update(committee=good)
        except:
            pass

        # Remove duplicate slugs.
        print 'removing duplicate slugs'
        slugs = list(Committee.objects.values_list('slug', flat=True).annotate(n=Count('slug')).filter(n__gt=1))
        for slug in slugs:
            bad, good = Committee.objects.filter(slug=slug).order_by('pk')
            bad.expenditure_set.all().update(committee=good)
            bad.contribution_set.all().update(committee=good)
            bad.delete()

        # denormalize
        print 'denormalizing candidate totals'
        for candidate in Candidate.objects.all():
            candidate.denormalize()

        # Remove amendmended filings
        print 'removing amended filings'
        for amendment in Expenditure.objects.exclude(amendment='N'):
            # Check for A2 amendments
            if amendment.amendment == 'A2':
                Expenditure.objects.filter(Q(amendment='N') | Q(amendment='A1'),
                                           transaction_id=amendment.transaction_id,
                                           committee=amendment.committee,
                                           expenditure_date=amendment.expenditure_date,
                                           candidate=amendment.candidate).delete()
            else:
                Expenditure.objects.filter(amendment='N',
                                           transaction_id=amendment.transaction_id,
                                           committee=amendment.committee,
                                           expenditure_date=amendment.expenditure_date,
                                           candidate=amendment.candidate).delete()


        # Remove more apparent duplicates
        """
        print 'removing more apparent duplicates'
        dupes = {}
        for expenditure in Expenditure.objects.all():
            e = Expenditure.objects.filter(candidate=expenditure.candidate,
                                           committee=expenditure.committee,
                                           expenditure_date=expenditure.expenditure_date,
                                           payee=expenditure.payee,
                                           ).exclude(filing_number=expenditure.filing_number)
            if e:
                d = []
                for i in e:
                    if round(i.expenditure_amount) == round(expenditure.expenditure_amount):
                        d.append(i)
                if d:
                    dupes[expenditure] = d

        for k, v in dupes.items():
            if Expenditure.objects.filter(pk=k.pk):
                for expenditure in v:
                    expenditure.delete()
        """


        cache.delete('buckley:widget2')
        cache.delete('buckley:totals')

        print 'caching totals'
        #cache_totals()


def get_candidate(data):
    #data = self.handle_special_cases(data)

    if not data['candidate_id']:
        candidate = lookup_candidate_by_name(data)
        if not candidate:
            return None
        else:
            return candidate

    candidate = lookup_candidate_in_crp_table(data['candidate_id'])
    if candidate:
        try:
            try:
                return Candidate.objects.get(crp_id=candidate['CID'])
            except Candidate.MultipleObjectsReturned:
                return Candidate.objects.get(crp_id=candidate['CID'],
                                             office=data['candidate_office'])
        except Candidate.DoesNotExist:
            return create_candidate_from_crp(candidate, data)

    try:
        try:
            return Candidate.objects.get(fec_id=data['candidate_id'])
        except Candidate.MultipleObjectsReturned:
            return Candidate.objects.get(fec_id=data['candidate_id'],
                                         office=data['candidate_office'])
    except Candidate.DoesNotExist:
        return create_candidate_from_fec(data)

    print 'could not find/create:', data['candidate_id'], data['candidate_first'], data['candidate_last']


def lookup_candidate_by_name(data):
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
            candidate = create_candidate_from_crp(dict(zip([x[0] for x in cursor.description], cursor.fetchone())), data)
        else:
            print 'not found:', data

        return None


def create_candidate_from_crp(candidate, data):
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
