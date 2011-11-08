import csv
import sys

from django.core.management.base import BaseCommand, CommandError

import MySQLdb
from django.conf import settings

#cursor = MySQLdb.Connection('reporting.sunlightfoundation.com', 'reporting', '***REMOVED***', 'reporting').cursor()
dbcfg = settings.DATABASES['default']
assert 'mysql' in dbcfg['ENGINE'].lower(), "The update_fec_crp_data command requires a MySQL database."
cursor = MySQLdb.Connection(dbcfg['HOST'], dbcfg['USER'], dbcfg['PASSWORD'], dbcfg['NAME']).cursor()


class Command(BaseCommand):
    args = '<table>'
    help = "Save CRP and FEC data to database"
    requires_model_validation = False

    def handle(self, *args, **options):
        table = args[0]

        if table in ('candidates', 'committees'):
            reader = csv.reader(sys.stdin, delimiter=',', quotechar='|')
            for row in reader:
                query = "INSERT INTO %s VALUES (%s)" % (table, ','.join(['%s']*len(row)))
                cursor.execute(query, row)

        else:
            if table == 'fec_candidate_master':
                fields = [('candidate_id', (1, 9)),
                          ('candidate_name', (10, 47)),
                          ('party1', (48, 50)),
                          #('filler', (51, 53)),
                          ('party3', (54, 56)),
                          ('seat_status', (57, 57)),
                          #('filler', (58, )),
                          ('candidate_status', (59, 59)),
                          ('street1', (60, 93)),
                          ('street2', (94, 127)),
                          ('city', (128, 145)),
                          ('state', (146, 147)),
                          ('zipcode', (148, 152)),
                          ('campaign_comm', (153, 161)),
                          ('election_year', (162, 163)),
                          ('current_district', (164, 163)), ]
            elif table == 'fec_committee_master':
                fields = [('committee_id', (1,9)),
                            ('committee_name', (10, 99)),
                            ('treasurer', (100, 137)),
                            ('street1', (138, 171)),
                            ('street2', (172, 205)),
                            ('city', (206, 223)),
                            ('state', (224, 225)),
                            ('zipcode', (226, 230)),
                            ('designation', (231, 231)),
                            ('type', (232, 232)),
                            ('party', (233, 235)),
                            ('filing_frequency', (236, 236)),
                            ('interest_group_category', (237, 237)),
                            ('connected_org_name', (238, 275)),
                            ('candidate_id', (276, 284)), ]

            for line in sys.stdin:
                data = []
                for fieldname, (start, end) in fields:
                    data.append(line[start-1:end].strip())

                query = "INSERT INTO %s VALUES (%s)" % (table, ('%s,' * len(data)).strip(','), )
                try:
                    cursor.execute(query, data)
                except MySQLdb.IntegrityError, (errcode, errtext):
                    if errcode == 1062:
                        print >>sys.stderr, errtext
                    else:
                        raise

