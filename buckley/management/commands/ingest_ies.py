import csv
import re
import sys
import time
import urllib
import urllib2

try:
    import json
except ImportError:
    import simplejson as json

from django.core.management.base import NoArgsCommand
from django.template.defaultfilters import slugify

from buckley.models import *

import name_tools
from name_tools.split import namecase
from dateutil.parser import parse as dateparse
import MySQLdb


cursor = MySQLdb.Connection('localhost', 'campfin', 'campfin', 'campfin').cursor()


def fec_master_lookup(id=None, name=None):
    if not id and not name:
        return None
    if id:
        cursor.execute("SELECT * FROM fec_candidate_master WHERE candidate_id = %s", id)
    elif name:
        cursor.execute("SELECT * FROM fec_candidate_master WHERE candidate_name = %s", name)
        if not cursor.rowcount:
            cursor.execute("SELECT * FROM fec_candidate_master WHERE candidate_name LIKE '%s%%'" % name)
    if not cursor.rowcount:
        return None
    return dict(zip([x[0] for x in cursor.description], cursor.fetchone()))


NAMES = {}
FEC_IDS = {}

def fixname(name):
    return re.sub(r'\([A-Z0-9]\)$', '', name).strip()

def td_lookup(name):
    time.sleep(.5)

    if name in NAMES:
        return NAMES[name]

    url = 'http://transparencydata.com/api/1.0/entities.json'
    body = urllib.urlencode({'apikey': '***REMOVED***', 'search': name})
    url += '?%s' % body
    print url
    data = urllib2.urlopen(url).read()
    try:
        j = json.loads(data)
    except ValueError:
        return name, '', ''
    data = [x for x in j if x['type'] == 'politician']
    if not data or len(data) > 1:
        NAMES[name] = '', '', ''
        return name, '', ''

    print len(data)

    # Cache the name
    td_name = fixname(data[0]['name'])
    NAMES[name] = [data[0]['name'], '', data[0]['party'], ]

    return data[0]['name'], '', data[0]['party']


def lookup_committee(fec_id):
    cursor.execute("SELECT pacshort FROM committees WHERE cmteid = %s", fec_id)
    if cursor.rowcount:
        return cursor.fetchone()[0]
    return None


class Command(NoArgsCommand):
    help = "Save independent expenditures to the database."
    requires_model_validation = False

    def handle_noargs(self, **options):
        # Clear data
        Committee.objects.all().delete()
        Candidate.objects.all().delete()
        Payee.objects.all().delete()
        Expenditure.objects.all().delete()

        reader = csv.DictReader(sys.stdin)

        for row in reader:
            if row['S_O_CAND_ID']:
                candidate = fec_master_lookup(id=row['S_O_CAND_ID'])
            else:
                candidate = fec_master_lookup(name=row['S_O_CAND_NM'])

            if candidate:
                row['party'] = candidate['party'][0]
                row['name'] = candidate['candidate_name']
                row['candidate_id'] = candidate['candidate_id']
            else:
                row['name'] = row['S_O_CAND_NM']
                row['party'] = ''
                row['candidate_id'] = row['S_O_CAND_ID']

            if not row['name']:
                row['name'] = 'No candidate listed'

            row['committee_name'] = lookup_committee(row['CMTE_ID']) or row['CMTE_NM']


            committee, created = Committee.objects.get_or_create(
                    #id=row['CMTE_ID'],
                    name=row['committee_name'],
                    slug=slugify(row['committee_name'])[:50]
                    )

            committee_id, created = CommitteeId.objects.get_or_create(fec_committee_id=row['CMTE_ID'], 
                                                                      committee=committee)
            #committee.committee_ids.add(committee_id)
            #committee.save()

            payee_name = row['PYE_NM'] or 'No payee listed'
            try:
                payee = Payee.objects.get(slug=slugify(payee_name)[:50])
            except Payee.DoesNotExist:
                payee, created = Payee.objects.get_or_create(
                        name=payee_name,
                        street1=row['PYE_ST1'],
                        street2=row['PYE_ST2'],
                        city=row['PYE_CITY'],
                        state=row['PYE_ST'],
                        zipcode=row['PYE_ZIP'],
                        slug=slugify(payee_name)[:50]
                        )

            try:
                #candidate = Candidate.objects.get(fec_id=row['candidate_id'])
                candidate = Candidate.objects.get(slug=slugify(row['name'])[:50])
            except Candidate.DoesNotExist:
                candidate = Candidate.objects.create(
                        fec_id=row['candidate_id'],
                        fec_name=namecase(row['name']),
                        crp_id=0,
                        crp_name='',
                        #crp_id=crp.id,
                        #crp_name=crp.name,
                        party=row['party'],
                        office=row['S_O_CAND_OFFICE'],
                        state=row['S_O_CAND_OFFICE_ST'],
                        district=row['S_O_CAND_OFFICE_DISTRICT'],
                        slug=slugify(row['name'])[:50]
                        )
            expenditure, created = Expenditure.objects.get_or_create(
                    image_number=row['IMAGE_NUM'],
                    form_type=row['FORM_TP'],
                    committee=committee,
                    payee=payee,
                    expenditure_form=row['EXP_TP'],
                    expenditure_purpose=row['EXP_PURPOSE'],
                    expenditure_date=dateparse(row['EXP_DT']) if row['EXP_DT'] else None,
                    expenditure_amount=float(row['EXP_AMT'].replace(',', '').replace('$', '') or 0),
                    support_oppose=row['S_O_IND'],
                    candidate=candidate,
                    transaction_id=row['TRAN_ID'],
                    memo_code=row['MEMO_CD'],
                    memo_text=row['MEMO_TEXT'],
                    receipt_date=dateparse(row['RECEIPT_DT']),
                    election_type=row['ELECTION_TP'],
                    election_year=row['FEC_ELECTION_YR']
                    )
            print expenditure
