from collections import defaultdict
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

from django.core.management.base import NoArgsCommand, BaseCommand, CommandError
from django.core.cache import cache
from django.db.models import Q

from buckley.models import *
from buckley.management.commands.cache_totals import cache_totals

from import_ies import committee_lookup, candidate_lookup_by_name, \
                       candidate_lookup_by_race, candidate_lookup_by_id, \
                       generic_querier

from dateutil.parser import parse as dateparse
from dateutil.tz import tzutc
import MySQLdb
from buckley import name_tools


# Names we know are missing/have the wrong FEC ID
FEC_ID_LOOKUP = {
        'S4MA00075': 'S0MA00075',
        'S4NH00235': 'S0NH00235',
        'H6NY21128': 'H6NY24128',
        'H4GA12159': 'H4GA12010',
        'H6NY23081': 'H0NY23081',
        }

NAME_LOOKUP = {
        'WILLIAM, HALTER': 'S0AR00168',
        'CONNOLLY, GERRY': 'H8VA11062',
        'HERSETH-SANDLIN, STEPHANIE': 'H2SD00092',
        'PERRIOELLO, TOM': 'H8VA05106',
        'Owens, Bill': 'H0NY23081',
        'Barrow, John': 'H4GA12010',
        'Arcuri, Michael': 'H6NY24128',
        }


def slugify(s):
    from django.template.defaultfilters import slugify as d_slugify
    return d_slugify(s)[:50]

def fec_committee_lookup(cid):
    query = "SELECT * FROM fec_committee_master WHERE committee_id = %s"
    params = [cid, ]
    return generic_querier(query, params)


def get_or_create_committee(name, id):
    committee, created = Committee.objects.get_or_create(
            name=name,
            slug=slugify(name))
    committe_id = CommitteeId.objects.create(
            fec_committee_id=id,
            committee=committee)
    return committee


def get_committee(row):
    id = row['CMTE_ID']
    committee = CommitteeId.objects.filter(fec_committee_id=id)
    if committee:
        return committee[0].committee

    committee = committee_lookup(id)
    if committee:
        return get_or_create_committee(committee['PACShort'], id)

    committee = fec_committee_lookup(id)
    if committee:
        return get_or_create_committee(committee['committee_name'], id)

    return get_or_create_committee(row['SPE_NAM'], id)


class Command(BaseCommand):
    args = '<override>'
    help = "Save electioneering data to the database."
    requires_model_validation = False

    def handle(self, *args, **options):
        url = 'ftp://ftp.fec.gov/FEC/ec_exp_2010.csv'

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
        #reader = list(csv.DictReader(open(r'/Users/bycoffe/tmp/ec_exp_2010.csv', 'r')))

        # THIS NO LONGER WORKS
        # First look through rows and create a dictionary
        # where the key is the group_id and the value
        # is a list of candidates associated with that
        # group_id. This allows us to determine which
        # candidates are associated with which disbursements.
        #group_ids = defaultdict(set)
        back_ref_ids = defaultdict(set)
        for row in reader:
            if row['SRC'].strip() in ('CAN', '94'):

                candidate = None

                if not row['CAND_ID']:
                    candidate_data = candidate_lookup_by_name(row['CAND_NM'])
                    row.update(candidate_data)
                    if not candidate_data:
                        candidate_data = candidate_lookup_by_race(row,
                                                             name_field='CAND_NM',
                                                             office_field='CAND_OFFICE',
                                                             district_field=None,
                                                             state_field='CAND_OFFICE_ST')
                        row.update(candidate_data)
                        if not candidate_data:
                            # If we get to this point and still can't
                            # identify the candidate, skip the record
                            #continue
                            #print row
                            #candidate = 'missing'
                            if row['CAND_NM'] in NAME_LOOKUP:
                                candidate_data = candidate_lookup_by_id(NAME_LOOKUP[row['CAND_NM']])
                                row['candidate_id'] = NAME_LOOKUP[row['CAND_NM']]
                                if candidate_data:
                                    row.update(candidate_data)
                                else:
                                    continue

                    # we have a candidate dict
                    if row.has_key('CID'):
                        # Lookup by CID
                        try:
                            candidate = Candidate.objects.get(crp_id=row['CID'])
                        except Candidate.DoesNotExist:
                            # Lookup by candidate_id
                            pass
                    elif row.get('candidate_id'):
                        try:
                            candidate = Candidate.objects.get(fec_id=row['candidate_id'])
                        except Candidate.DoesNotExist:
                            pass
                    elif row.get('CAND_NM'):
                        # Look up by FEC name
                        try:
                            candidate = Candidate.objects.get(fec_name=row['CAND_NM'])
                        except Candidate.DoesNotExist:
                            pass

                else:
                    if row['CAND_ID'] in FEC_ID_LOOKUP:
                        row['CAND_ID'] = FEC_ID_LOOKUP[row['CAND_ID']]

                    try:
                        candidate = Candidate.objects.get(fec_id=row['CAND_ID'])
                    except Candidate.DoesNotExist:
                        if row.get('candidate_id'):
                            row.update(candidate_lookup_by_id(row['CAND_ID']))
                            id_field = 'candidate_id'
                        elif row.get('CAND_ID'):
                            row.update(candidate_lookup_by_id(row['CAND_ID']))
                            id_field = 'CAND_ID'

                        try:
                            candidate = Candidate.objects.get(fec_id=row[id_field])
                        except Candidate.DoesNotExist:
                            pass

                if not candidate and not row.get('FirstLastP', None):
                    try:
                        candidate = Candidate.objects.get(fec_id=row['candidate_id'])
                    except (Candidate.DoesNotExist, Candidate.MultipleObjectsReturned):
                        print row
                        continue
                    #continue

                if not candidate:
                    state = row['CAND_OFFICE_ST']
                    if not state:
                        state = row.get('DistIDRunFor', '')[:2]

                    district = row.get('DistIDRunFor', '')[2:]

                    candidate_name = row.get('FirstLastP', row.get('CAND_NM', ''))
                    crp_name = re.sub(r'\s\([A-Z0-9]\)', '', candidate_name)

                    if row.get('CID', None):
                        try:
                            candidate = Candidate.objects.get(crp_id=row['CID'])
                        except Candidate.DoesNotExist:
                            pass

                    if not candidate:
                        candidate = Candidate.objects.create(
                                fec_id=row['CAND_ID'],
                                fec_name=row['CAND_NM'],
                                crp_id=row.get('CID', ''),
                                crp_name=crp_name,
                                party=row.get('Party', ''),
                                office=row['CAND_OFFICE'],
                                state=state,
                                district=district,
                                slug=slugify(candidate_name))

                #group_ids[(row['CMTE_ID'], row['GROUP_ID'])].add(candidate)
                back_ref_ids[(row['CMTE_ID'], row['FILE_NUM'], row['BACK_REF_TRAN_ID'])].add(candidate)


        for row in reader:
            if row['SRC'].strip() in ('SB', '93'): # An expenditure report

                if not row['FILE_NUM']:
                    continue

                # Check which candidates this row's
                # group_id corresponds to.
                #candidates = group_ids[(row['CMTE_ID'], row['GROUP_ID'])]
                candidates = back_ref_ids[(row['CMTE_ID'], row['FILE_NUM'], row['TRAN_ID'])]

                # Some communications don't have a candidate
                # associated with them. Skip these.
                if not candidates:
                    continue

                image_number = int(Decimal(row['IMAGENO']))
                committee = get_committee(row)
                try:
                    payee = Payee.objects.get(slug=slugify(row['PAY']))
                except Payee.DoesNotExist:
                    payee = Payee.objects.create(name=row['PAY'].strip(','),
                                                slug=slugify(row['PAY']))
                expenditure_purpose = row['PUR']
                expenditure_date = dateparse(row['EXP_DAT'])
                expenditure_amount = Decimal(row['EXP_AMO'].replace(',', ''))
                support_oppose = '' # Don't have this for electioneering
                election_type = row['ELE_TYP'].lower()
                if election_type == 'general':
                    election_type = 'G'
                elif election_type == 'primary':
                    election_type = 'P'
                else:
                    election_type = 'O'

                transaction_id = row['TRAN_ID']
                receipt_date = dateparse(row['RECEIPT_DT'])
                filing_number = row['FILE_NUM'].replace(',', '')
                amendment = row['AMNDT_IND']
                if amendment != 'N':
                    continue

                # Sometimes the candidates in this expenditure
                # are from different races. If that's the case,
                # we leave the race field blank.
                race = ''
                if len(set([x.race() for x in candidates])) == 1:
                    race = list(candidates)[0].race()

                electioneering_commication = True

                # These are electioneering comms
                # that were already filed as IEs
                x = committee.expenditure_set.filter(expenditure_amount=expenditure_amount,
                        expenditure_date=expenditure_date,
                        electioneering_communication=False
                        )
                if x:
                    print 'ALREADY IN DB AS IE %s' % row['FILE_NUM']
                    continue

                # These are committees that have also filed
                # IE reports
                #if committee.expenditure_set.count():
                #    print committee

                try:
                    expenditure = Expenditure.objects.get(
                            image_number=image_number,
                            transaction_id=transaction_id)

                    # In case the FEC has updated its data
                    expenditure.committee = committee
                    expenditure.payee = payee
                    expenditure.expenditure_purpose = expenditure_purpose
                    expenditure.expenditure_date = expenditure_date
                    expenditure.expenditure_amount = expenditure_amount
                    expenditure.receipt_date = receipt_date
                    expenditure.election_type = election_type
                    expenditure.filing_number = filing_number
                    expenditure.amendment = amendment
                    expenditure.race = race
                    expenditure.save()

                except Expenditure.DoesNotExist:
                    expenditure = Expenditure.objects.create(
                            image_number=image_number,
                            transaction_id=transaction_id,
                            committee=committee,
                            payee=payee,
                            expenditure_purpose=expenditure_purpose,
                            expenditure_date=expenditure_date,
                            expenditure_amount=expenditure_amount,
                            receipt_date=receipt_date,
                            election_type=election_type,
                            filing_number=filing_number,
                            amendment=amendment,
                            race=race,
                            electioneering_communication=True
                            )

                expenditure.electioneering_candidates.add(*candidates)

                #print expenditure

        # Remove amendmended filings
        """
        print 'Removing amended filings'
        for amendment in Expenditure.objects.exclude(amendment='N', electioneering_communication=True):
            # Check for A2 amendments
            if amendment.amendment == 'A2':
                Expenditure.objects.filter(Q(amendment='N') | Q(amendment='A1'),
                                           transaction_id=amendment.transaction_id, 
                                           committee=amendment.committee, 
                                           electioneering_communication=True,
                                           candidate=amendment.candidate).delete()
            else:
                Expenditure.objects.filter(amendment='N', 
                                           transaction_id=amendment.transaction_id, 
                                           committee=amendment.committee, 
                                           electioneering_communication=True,
                                           candidate=amendment.candidate).delete()
        """

        # Remove more apparent duplicates
        """
        print 'removing more apparent duplicates'
        dupes = {}
        for expenditure in Expenditure.objects.filter(electioneering_communication=False):
            e = Expenditure.objects.filter(candidate=expenditure.candidate,
                                           committee=expenditure.committee,
                                           expenditure_date=expenditure.expenditure_date,
                                           payee=expenditure.payee,
                                           electioneering_communication=False
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


        # Denormalize expensive-to-calculate fields
        print 'Denormalizing candidates'
        for candidate in Candidate.objects.all():
            candidate.denormalize()

        # Clear the cached widget
        cache.delete('buckley:widget2')

        #print 'caching totals'
        cache_totals()
