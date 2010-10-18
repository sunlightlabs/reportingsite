from cStringIO import StringIO
import csv
import datetime
from decimal import Decimal
import logging
import os
import re
import socket
import sys
import time
import urllib
import urllib2

try:
    import json
except ImportError:
    import simplejson as json

from django.core.cache import cache
from django.core.mail import send_mail
from django.core.management.base import NoArgsCommand, BaseCommand, CommandError
from django.db.models import Q
from django.template.defaultfilters import slugify

from buckley.models import *

from dateutil.parser import parse as dateparse
from dateutil.tz import tzutc
import MySQLdb
from buckley import name_tools


# So our HTTP requests don't timeout as quickly
socket.setdefaulttimeout(25)

logging.basicConfig(filename='ie_import_errors.log', level=logging.DEBUG)


#cursor = MySQLdb.Connection('reporting.sunlightfoundation.com', 'reporting', '***REMOVED***', 'reporting').cursor()
cursor = MySQLdb.Connection('localhost', 'reporting', '***REMOVED***', 'reporting').cursor()

# Some names we know are missing FEC IDs.
NAME_LOOKUP = {
    'Altmire, Jason': 'H6PA04110',
    'Boozman, John': 'S0AR00150',
    'BOXER, BARBARA': 'S2CA00286',
    'BUCHANAN, JOAN': 'H0CA10099',
    'Carnahan, Russ': 'H0MO00019',
    'Chabot, Steve': 'H8OH01043',
    'CHU, BETTY': 'H0CA32218',
    'Edwards, Chet': 'H8TX06035',
    'FIORINA, CARLY': 'S0CA00330',
    'HALTER, WILLIAM A': 'S0AR00168',
    'HAWKINS, B LEE': 'H0GA09089',
    'Hayworth, Nan': 'H0NY19139',
    'Kelly, Jesse': 'H0AZ08015',
    'KIRKLAND, RONALD': 'H0TN08261',
    'Kirkpatrick, Ann': 'H8AZ01104',
    'LASSA, JULIE': 'H0WI07069',
    'LINCOLN, BLANCHE': 'S8AR00112',
    'LINCOLN, BLANCHE L': 'S8AR00112',
    'Martin, Edward': 'H0MO03112',
    'Paton, Jonathan': 'H0AZ08056',
    'Portman, Rob': 'S0OH00133',
    'ROMANOFF, ANDREW': 'S0CO00286',
    'SESTAK, JOE': 'S0PA00434',
    'Sestak, Joe': 'S0PA00434',
    'STUTZMAN, MARLIN': 'S0IN00095',
    'SIMPSON, MIKE': 'H4FL01122',
    'COEHRING, BRAD': 'H0CA11303',
    'POMBO, RICHARD W.': 'H2CA11051',
    'CAMPBELL FOR US SENATE': 'S2CA00351',
    'PORGESON, CHUCK': 'S0MO00191',
    'HUIZENGA, BILL': 'H0MI02094',
    'Peter, Gary': 'H8MI09068',
    'Herseth Sandlin, Stephanie': 'H2SD00092',
    'ROONEY, BRIAN': 'H0MI07077',
}

def generic_querier(query, params, multirows=False):
    cursor.execute(query, params)
    if cursor.rowcount:
        if multirows:
            fields = [x[0] for x in cursor.description]
            return [dict(zip(fields, x)) for x in cursor.fetchall()]
        else:
            return dict(zip([x[0] for x in cursor.description], cursor.fetchone()))
    else:
        if multirows:
            return []
        else:
            return {}

def committee_lookup(id):
    query = "SELECT * FROM committees WHERE cmteid = %s ORDER BY cycle DESC LIMIT 1"
    params = [id, ]
    return generic_querier(query, params)


def candidate_lookup_by_name(name):
    query = "SELECT * FROM fec_candidate_master WHERE candidate_name = %s"
    params = [name, ]
    return generic_querier(query, params)


def td_candidate_lookup(name):
    """Look up a candidate by name in Transparency Data
    """
    time.sleep(.5)
    body = urllib.urlencode({'apikey': '***REMOVED***', 'search': name})
    url = 'http://transparencydata.com/api/1.0/entities.json?%s' % body
    print url
    data = urllib2.urlopen(url).read()
    try:
        j = json.loads(data)
    except ValueError:
        return name, '', ''
    data = [x for x in j if x['type'] == 'politician']
    if not data or len(data) > 1:
        return None

    query = "SELECT * FROM candidates WHERE firstlastp = %s"
    params = [data[0]['name'],]
    return generic_querier(query, params)
    #return data[0]['name']


def candidate_lookup_by_id(fec_id):
    query = "SELECT * FROM candidates WHERE feccandid = %s ORDER BY cycle desc LIMIT 1"
    params = [fec_id, ]
    return generic_querier(query, params)


def candidate_lookup_by_race(row, name_field='CAND_NAM', office_field='CAN_OFF',
        district_field='CAN_OFF_DIS', state_field='CAN_OFF_STA'):
    office = row[office_field]
    district = row.get(district_field, '')
    state = row[state_field]
    prefix, first, last, suffix = name_tools.split(row[name_field])
    if office == 'H':
        if district:
            query = "SELECT * FROM candidates WHERE distidrunfor = %s AND cycle = 2010 AND firstlastp LIKE %s"
            params = ['%s%s' % (state, district),
                      '%' + last + '%', ]
        else:
            query = "SELECT * FROM candidates WHERE distidrunfor LIKE %s AND cycle = 2010 AND firstlastp LIKE %s"
            params = [state + '%', '%' + last + '%', ]

    elif office == 'S':
        query = "SELECT * FROM candidates WHERE distidrunfor LIKE %s AND cycle = 2010 AND firstlastp LIKE %s"
        params = ['%sS' % state + '%',
                  '%' + last + '%', ]
    else:
        return None
    return generic_querier(query, params)


class Command(BaseCommand):
    args = '<override>'
    help = "Save independent expenditures to the database."
    requires_model_validation = False

    def handle(self, *args, **options):
        """
        can_id - ID number for the candidate referenced in the spending
        cand_nam - name of the candidate (as it was provided in the report)
        spe_id - ID number of the committee or group making the disbursement
        spe_nam - name of the committee or group or person making the disbursement
        ele_typ - election type - e.g. G=general, P=primary, S=special
        can_off_sta - candidate state abbreviation
        can_off_dis - candidate district
        can_off - candidate office sought (H=House, S=Senate)
        cand_pty_affiliation - candidate party
        exp_amo - specific expenditure amount
        exp_dat - expenditure date
        agg_amo - aggregate from this spender in this race
        sup_opp - S=support O=oppose the candidate
        pur - purpose of the disbursement
        pay - payee
        tran_id - transaction identifier (unique within the filing)
        image_num - image number for the transaction (i.e. location where the entry can be viewed)
        receipt_dt - receipt date for the submission
        """
        #Committee.objects.all().delete()
        #Candidate.objects.all().delete()
        #Payee.objects.all().delete()
        #Expenditure.objects.all().delete()

        url = 'ftp://ftp.fec.gov/FEC/ind_exp_2010.csv'

        if not args:
            # Check whether the FEC data has been updated in the past hour.
            # Having trouble getting urllib2 or httplib2 headers
            # to show last-modified time for a file on an FTP server,
            # so using cURL.
            headers = os.popen('curl -Is "%s"' % url).read().split('\n')
            last_modified = dateparse(headers[0].replace('Last-Modified: ', '').strip())
            hours_diff = (datetime.datetime.now(tzutc()) - last_modified).seconds / 60 / 60

            # If data hasn't been updated in the past hour, don't do anything.
            if hours_diff > 1:
                return

        reader = list(csv.DictReader(StringIO(urllib2.urlopen(url).read())))
        #reader = csv.DictReader(open(r'/Users/bycoffe/testcsv.csv', 'r'))

        committees = {}
        candidates = {}
        candidates_by_name = {}
        skipped = []

        for row in reader:

            if not row['EXP_DAT']:
                continue

            if row['CAN_OFF'] not in ('H', 'S'):
                continue

            expenditure_date = dateparse(row['EXP_DAT'])
            if expenditure_date.date() < datetime.date(2009, 1, 1) or expenditure_date.date() > datetime.date.today():
                continue

            if not row['CAND_NAM'] and not row['CAN_ID']:
                continue

            # If the name is in our lookup dict, use the ID from there.
            if row['CAND_NAM'] in NAME_LOOKUP:
                row['CAN_ID'] = NAME_LOOKUP[row['CAND_NAM']]

            # We know that this candidate ID is wrong in the CSV
            if row['CAND_NAM'] == 'BUCHANAN, JOAN':
                row['CAN_ID'] = NAME_LOOKUP[row['CAND_NAM']]
            if row['CAND_NAM'] == 'Edwards, Chet':
                row['CAN_ID'] = NAME_LOOKUP[row['CAND_NAM']]

            try:
                committee_id = CommitteeId.objects.get(fec_committee_id=row['SPE_ID'])
                if committee_id:
                    committee = committee_id.committee
            except CommitteeId.DoesNotExist:
                committee = committee_lookup(row['SPE_ID'])
                row.update(committee)
                #committee_name = row['PACShort'].strip() if row.has_key('PACShort') else row['SPE_NAM'].strip().title()
                if row.get('PACShort', '').strip():
                    committee_name = row['PACShort'].strip()
                else:
                    committee_name = row['SPE_NAM'].strip().title()

                committee, created = Committee.objects.get_or_create(
                        name=committee_name,
                        slug=slugify(committee_name)[:50]
                    )
                committee_id = CommitteeId.objects.create(
                        fec_committee_id=row['SPE_ID'],
                        committee=committee)

            #print committee

            row['CAND_NAM'] = re.sub(r'\s*,\s*$', '', row['CAND_NAM']) # Remove trailing comma + whitespace
            row['CAND_NAM'] = re.sub(r'\(\w\w\)', '', row['CAND_NAM']) # Remove parenthesized state

            try:
                if not row['CAN_ID']:
                    raise Candidate.DoesNotExist()
                candidate = Candidate.objects.get(fec_id=row['CAN_ID'])
            except Candidate.DoesNotExist:
                candidate = candidate_lookup_by_id(row['CAN_ID'])
                if candidate:
                    candidates[id] = candidate
                row.update(candidate)

                # Look up the candidate
                if not row['CAN_ID'] or row['CAN_ID'] not in candidates:
                    if row['CAND_NAM'] not in candidates_by_name:
                        name = candidate_lookup_by_name(row['CAND_NAM'])
                        if not name:
                            # Look up name in Transparency Data
                            if not name:

                                # Look up by last name and race
                                name = candidate_lookup_by_race(row)
                                if not name:
                                    #logging.debug('Could not find candidate for image number %s transaction id %s' % (row['IMAGE_NUM'], row['TRAN_ID']))
                                    #logging.debug(row)
                                    skipped.append(row)
                                    continue
                                else:
                                    candidates_by_name[row['CAND_NAM']] = name

                            else:
                                candidates_by_name[row['CAND_NAM']] = name

                        else:
                            candidates_by_name[row['CAND_NAM']] = name
                    else:
                        name = candidates_by_name[row['CAND_NAM']]

                    row.update(name)

                crp_name = re.sub(r'\s\([A-Z0-9]\)', '', row.get('FirstLastP', ''))
                if crp_name:
                    candidate_name = crp_name
                else:
                    candidate_name = ('%s %s %s %s' % name_tools.split(row['CAND_NAM'])).strip()

                candidate_slug = slugify(candidate_name)[:50]

                try:
                    candidate = Candidate.objects.get(slug=candidate_slug)
                except Candidate.DoesNotExist:
                    party = ''
                    if row.has_key('Party'):
                        party = row['Party']
                    else:
                        if row['CAND_PTY_AFFILIATION'].startswith('REPUBLICAN'):
                            party = 'R'
                        elif row['CAND_PTY_AFFILIATION'].startswith('DEMOCRAT'):
                            party = 'D'

                    state = ''
                    district = ''
                    if row.has_key('DistIDRunFor'):
                        state = row['DistIDRunFor'][:2]
                        district = row['DistIDRunFor'][-2:]
                    else:
                        state = row['CAN_OFF_STA']
                        district = row['CAN_OFF_DIS']

                    candidate = None
                    if row.has_key('CID'):
                        try:
                            candidate = Candidate.objects.get(crp_id=row['CID'])
                        except Candidate.DoesNotExist:
                            if row.get('CAN_ID', None):
                                try:
                                    candidate = Candidate.objects.get(fec_id=row['CAN_ID'])
                                except Candidate.DoesNotExist:
                                    pass
                            elif row.get('CAND_NAM', None):
                                try:
                                    candidate = Candidate.objects.get(fec_name=row['CAND_NAM'])
                                except Candidate.DoesNotExist:
                                    pass

                    if not candidate:
                        candidate = Candidate.objects.create(
                                fec_id=row['CAN_ID'],
                                fec_name=row['CAND_NAM'],
                                crp_id=row.get('CID', ''),
                                crp_name=crp_name,
                                party=party,
                                office=row['CAN_OFF'],
                                state=state,
                                district=district,
                                slug=slugify(candidate_name)[:50]
                            )

            #print candidate

            try:
                payee = Payee.objects.get(slug=slugify(row['PAY'])[:50])
            except Payee.DoesNotExist:
                payee = Payee.objects.create(
                        name=row['PAY'],
                        slug=slugify(row['PAY'])[:50])

            #print payee

            row['IMAGE_NUM'] = row['IMAGE_NUM'].replace(',', '')

            try:
                expenditure = Expenditure.objects.get(
                        image_number=int(Decimal(row['IMAGE_NUM'])),
                        transaction_id=row['TRAN_ID']
                        )

                # In case the FEC has updated its data
                expenditure.committee = committee
                expenditure.payee = payee
                expenditure.expenditure_purpose = row['PUR']
                expenditure.expenditure_date = expenditure_date
                expenditure.expenditure_amount=Decimal(row['EXP_AMO'].replace(',', ''))
                expenditure.support_oppose=row['SUP_OPP']
                expenditure.candidate=candidate
                expenditure.receipt_date=dateparse(row['RECEIPT_DT']).date()
                expenditure.election_type=row['ELE_TYP']
                expenditure.filing_number = int(Decimal(row['FILE_NUM'].replace(',', '')))
                expenditure.amendment = row['AMNDT_IND']
                expenditure.race = expenditure.candidate.race()
                expenditure.save()

            except Expenditure.DoesNotExist:
                expenditure = Expenditure.objects.create(
                        image_number=int(Decimal(row['IMAGE_NUM'])),
                        committee=committee,
                        payee=payee,
                        expenditure_purpose=row['PUR'],
                        expenditure_date=expenditure_date,
                        expenditure_amount=Decimal(row['EXP_AMO'].replace(',', '')) if row['EXP_AMO'] else 0,
                        support_oppose=row['SUP_OPP'],
                        election_type=row['ELE_TYP'],
                        candidate=candidate,
                        transaction_id=row['TRAN_ID'],
                        filing_number=int(Decimal(row['FILE_NUM'].replace(',', ''))),
                        amendment=row['AMNDT_IND'],
                        receipt_date=dateparse(row['RECEIPT_DT']).date(),
                        race=candidate.race()
                        )

            print expenditure.id

        for row in skipped:

            # Duplicated code
            try:
                committee_id = CommitteeId.objects.get(fec_committee_id=row['SPE_ID'])
                if committee_id:
                    committee = committee_id.committee
            except CommitteeId.DoesNotExist:
                committee = committee_lookup(row['SPE_ID'])
                row.update(committee)
                if row.get('PACShort', '').strip():
                    committee_name = row['PACShort'].strip()
                else:
                    committee_name = row['SPE_NAM'].strip().title()

                committee, created = Committee.objects.get_or_create(
                        name=committee_name,
                        slug=slugify(committee_name)[:50]
                    )
                committee_id = CommitteeId.objects.create(
                        fec_committee_id=row['SPE_ID'],
                        committee=committee)


            if 'CID' in row: # A CRP ID had been found earlier
                crp_name = re.sub(r'\s\([A-Z0-9]\)', '', row.get('FirstLastP', ''))
                try:
                    candidate = Candidate.objects.get(crp_id=row['CID'])
                except Candidate.DoesNotExist:
                    #logging.debug('Skipped record because candidate does not exist: ' + str(row))
                    crp_name=re.sub(r'\s\([A-Z0-9]\)', '', row['FirstLastP'])
                    candidate = Candidate.objects.create(
                            fec_id=row['CAN_ID'],
                            fec_name=row['CAND_NAM'],
                            crp_id=row['CID'],
                            crp_name=crp_name,
                            party=row['Party'],
                            office=row['CAN_OFF'],
                            state=row['DistIDRunFor'][:2],
                            district=row['DistIDRunFor'][2:],
                            slug=slugify(crp_name)[:50]
                            )

                try:
                    payee = Payee.objects.get(slug=slugify(row['PAY'])[:50])
                except Payee.DoesNotExist:
                    payee = Payee.objects.create(
                            name=row['PAY'],
                            slug=slugify(row['PAY'])[:50])

                row['IMAGE_NUM'] = row['IMAGE_NUM'].replace(',', '')

                try:
                    expenditure = Expenditure.objects.get(
                            image_number=int(Decimal(row['IMAGE_NUM'])),
                            transaction_id=row['TRAN_ID']
                            )

                    """ This needs to go in a separate function to avoid duplication in this code """
                    # In case the FEC has updated its data
                    expenditure.committee = committee
                    expenditure.payee = payee
                    expenditure.expenditure_purpose = row['PUR']
                    expenditure.expenditure_date = dateparse(row['EXP_DAT'])
                    expenditure.expenditure_amount=Decimal(row['EXP_AMO'].replace(',', ''))
                    expenditure.support_oppose=row['SUP_OPP']
                    expenditure.candidate=candidate
                    expenditure.receipt_date=dateparse(row['RECEIPT_DT']).date()
                    expenditure.election_type=row['ELE_TYP']
                    expenditure.filing_number = int(Decimal(row['FILE_NUM'].replace(',', '')))
                    expenditure.amendment = row['AMNDT_IND']
                    expenditure.race = expenditure.candidate.race()
                    expenditure.save()

                except Expenditure.DoesNotExist:
                    expenditure = Expenditure.objects.create(
                            image_number=int(Decimal(row['IMAGE_NUM'])),
                            committee=committee,
                            payee=payee,
                            expenditure_purpose=row['PUR'],
                            expenditure_date=dateparse(row['EXP_DAT']),
                            expenditure_amount=Decimal(row['EXP_AMO'].replace(',', '')) if row['EXP_AMO'] else 0,
                            support_oppose=row['SUP_OPP'],
                            election_type=row['ELE_TYP'],
                            candidate=candidate,
                            transaction_id=row['TRAN_ID'],
                            filing_number=int(Decimal(row['FILE_NUM'].replace(',', ''))),
                            amendment=row['AMNDT_IND'],
                            receipt_date=dateparse(row['RECEIPT_DT']).date(),
                            race=candidate.race()
                            )

            else:
                logging.debug('Skipped record because no CID:' + str(row))

        # Remove amendmended filings
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


        # Remove apparent duplicates
        for expenditure in Expenditure.objects.all():
            e = Expenditure.objects.filter(candidate=expenditure.candidate,
                                           committee=expenditure.committee,
                                           expenditure_date=expenditure.expenditure_date,
                                           payee=expenditure.payee,
                                           expenditure_amount=str(round(expenditure.expenditure_amount))).exclude(filing_number=expenditure.filing_number)
            if e.count() > 1:
                for to_delete in e[1:]:
                    to_delete.delete()

        # Remove more apparent duplicates
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

        # End removing more apparent duplicates

        send_mail('[ IE data importer ] Data updated',
                  'Database contains %s expenditure records' % str(Expenditure.objects.count()),
                  'abycoffe@sunlightfoundation.com',
                  ['abycoffe@sunlightfoundation.com', ],
                  fail_silently=True)

        # Remove clear errors
        Expenditure.objects.filter(image_number=10930676766, candidate__slug='nick-rahall').delete()
        Expenditure.objects.filter(image_number=10931302159).delete()

        # Fix Murkowski problem
        def fix_murkowski():
            frank = Candidate.objects.filter(slug='frank-h-murkowski')
            if not frank:
                return
            frank = frank[0]

            lisa = Candidate.objects.filter(slug='lisa-murkowski')
            if not lisa:
                return
            lisa = lisa[0]
            frank.expenditure_set.update(candidate=lisa)
            frank.delete()

        fix_murkowski()

        # Fix support/oppose errors
        Expenditure.objects.filter(image_number=10990630854, candidate__slug='blanche-lincoln').update(support_oppose='O')
        Expenditure.objects.filter(image_number=10931242198, candidate__slug='ann-mclane-kuster').update(support_oppose='S')
        Expenditure.objects.filter(image_number=10931249349, candidate__slug='macdonald-king-dalessandro').update(support_oppose='S')
        Expenditure.objects.filter(image_number=10990639760, candidate__slug='sharron-e-angle').update(support_oppose='S')
        Expenditure.objects.filter(image_number__in=[10990653705, 10990653694], candidate__slug='alan-b-mollohan').update(support_oppose='O')
        Expenditure.objects.filter(image_number__in=[10991169349, 10991169350, 10991169350], candidate__slug='pat-toomey').update(support_oppose='O')
        Expenditure.objects.filter(image_number__in=[10991180834, 10991180834, 10991180834, 10991180842, 10991180822, 10991180822, 10991180835], candidate__slug='joseph-a-sestak-jr').update(support_oppose='S')
        Expenditure.objects.filter(image_number__in=[10991225146, 10991124434, 10991124436, 10931094398, 10931135624, 10931094385, 10931094382, 10931094380, 10030273417], candidate__slug__in=['paul-w-hodes', 'robin-w-carnahan', 'bill-halter', ]).update(support_oppose='S')
        Expenditure.objects.filter(image_number=10930395723, candidate__slug='robert-f-bennett').update(support_oppose='O')

        Expenditure.objects.filter(image_number=10931278251, candidate__slug='tim-griffin').update(support_oppose='O')
        Expenditure.objects.filter(image_number=10931278248, candidate__slug='joyce-elliott').update(support_oppose='S')

        # Remove committees that have no expenditures
        for committee in Committee.objects.all():
            if committee.expenditure_set.count() == 0:
                committee.delete()

        # Remove candidates that have no expenditures
        for candidate in Candidate.objects.all():
            if candidate.expenditure_set.count() == 0:
                candidate.delete()

        # Denormalize expensive-to-calculate fields
        for candidate in Candidate.objects.all():
            candidate.denormalize()

        # Clear the cached widget
        cache.delete('buckley:widget2')

        cache.delete('buckley:totals')
