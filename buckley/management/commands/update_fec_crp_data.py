import csv
import sys

from django.core.management.base import BaseCommand, CommandError

import MySQLdb

cursor = MySQLdb.Connection('reporting.sunlightfoundation.com', 'reporting', '***REMOVED***', 'reporting').cursor()


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

            for line in sys.stdin:
                data = []
                for fieldname, (start, end) in fields:
                    data.append(line[start-1:end].strip())

                query = "INSERT INTO fec_candidate_master VALUES (%s)" % ('%s,' * len(data)).strip(',')
                try:
                    cursor.execute(query, data)
                except MySQLdb.IntegrityError:
                    continue
