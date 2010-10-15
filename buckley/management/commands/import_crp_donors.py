import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from buckley.models import Committee, Contribution, CommitteeId

from dateutil.parser import parse as dateparse
import MySQLdb


MIN_DATE = datetime.date(2009, 1, 1)

cursor = MySQLdb.Connection('localhost', 'reporting', '***REMOVED***', 'reporting').cursor()


def get_527_committees():
    for committee_id in CommitteeId.objects.all():
        cursor.execute("SELECT DISTINCT EIN FROM cmtes527 WHERE CmteID = %s AND cycle = 2010", [committee_id.fec_committee_id, ])
        if cursor.rowcount:
            for ein in cursor.fetchall():
                yield committee_id, ein[0]


def get_527_contributions(ein):
    cursor.execute("SELECT * FROM rcpts527 WHERE RecipID = %s AND Date >= '2009-01-01'", [ein, ])
    for row in cursor.fetchall():
        yield dict(zip([x[0] for x in cursor.description], row))


def save_527_contribution(committee, contribution):
    try:
        contribution = Contribution.objects.create(
                            committee=committee,
                            filing_number=contribution['ID'],
                            name=contribution['Contrib'],
                            date=contribution['Date'],
                            employer=contribution['Employer'],
                            occupation=contribution['Occupation'],
                            street1='',
                            street2='',
                            city=contribution['City'],
                            state=contribution['State'],
                            zipcode=contribution['Zip'],
                            amount=str(contribution['Amount']),
                            aggregate=str(contribution['YTD']),
                            memo='',
                            url='')
    except IntegrityError:
        return None

    return contribution


def get_fec_contributions(committee_id):
    cursor.execute("SELECT * FROM individuals10 WHERE recipid = %s AND cycle = 2010", [committee_id.fec_committee_id, ])
    for row in cursor.fetchall():
        yield dict(zip([x[0] for x in cursor.description], row))


def save_fec_contribution(committee, contribution):
    """
    {'City': 'WASHINGTON', 'Zip': '20005', 'Orgname': '', 'ContribID': 'j1001430872 ', 'State': 'DC', 'Type': '15 ', 'OtherID': '', 'RecipCode': 'PL', 'CmteID': 'C00004036', 'Microfilm': '10930745518', 'FECTransID': '1464786', 'FecOccEmp': 'SEIU/EXECUTIVE BOARD MEM', 'Date': '04/30/2010', 'UltOrg': '', 'Gender': 'F', 'Amount': '202', 'Occ_EF': 'Executive Board Mem', 'RecipID': 'C00004036', 'Source': 'P/PAC', 'RealCode': 'LG300', 'Street': '1519 - 12th St Nw', 'Emp_EF': 'SEIU', 'Contrib': 'HENRY, MARY KAY', 'Cycle': '2010'}
    """
    try:
        contribution = Contribution.objects.create(
                committee=committee,
                filing_number=contribution['FECTransID'],
                name=contribution['Contrib'],
                date=dateparse(contribution['Date']),
                employer=contribution['Orgname'],
                occupation=contribution['Occ_EF'],
                street1=contribution['Street'],
                street2='',
                city=contribution['City'],
                state=contribution['State'],
                zipcode=contribution['Zip'],
                amount=contribution['Amount'],
                aggregate=0,
                memo='',
                url=''
                )
    except IntegrityError:
        print 'Skipping'
        return None

    return contribution


class Command(BaseCommand):

    def handle(self, *args, **options):
        for committee_id, ein in get_527_committees():
            for row in get_527_contributions(ein):
                contribution = save_527_contribution(committee_id.committee, row)
                print contribution

        for committee_id in CommitteeId.objects.all():
            for row in get_fec_contributions(committee_id):
                try:
                    contribution = save_fec_contribution(committee_id.committee, row)
                except:
                    print 'Error: %s' % str(row)
                print committee_id.committee, contribution
