import datetime
from collections import defaultdict
from operator import itemgetter
import sys

from pymongo import Connection

from django.core.management.base import BaseCommand, CommandError

from doddfrank.views import UnicodeWriter


class Command(BaseCommand):

    def handle(self, *args, **options):
        collection = Connection().test.meetings
        agencies = collection.distinct(key='agency')

        writer = UnicodeWriter(sys.stdout)
        writer.writerow(('name', 'agency', 'total_meetings', 'months', 'avg. meetings/month',))

        staffers_by_agency = []

        for agency in agencies:
            first_meeting = collection.find({'agency': agency}, fields=['meeting_time',]).sort([('meeting_time', 1),]).next()
            date = first_meeting['meeting_time'].date()

            if date.day > 15:
                start = (date + datetime.timedelta(30))
                start_month = start.month
                start_year = start.year
                start_day = 1
            else:
                start_month = date.month
                start_year = date.year
                start_day = 1

            start = datetime.datetime(start_year, start_month, start_day, 0, 0)
            if agency == 'SEC':
                start = datetime.datetime(2010, 7, 1, 0, 0)

            end = datetime.datetime(2011, 6, 30, 0, 0)
            if agency == 'Treasury':
                end = datetime.datetime(2011, 5, 30, 0, 0)

            meetings = collection.find({'meeting_time': {'$gte': start, '$lte': end}, 'agency': agency})
            days = (end - start).days
            month_periods = days / 30

            if agency == 'CFTC':
                staffers = defaultdict(int)
                for meeting in meetings:
                    for person in set(meeting.get('cftc_staff', [])):
                        staffers[person] += 1

                #staffers_by_agency.append((staffer, agency, count))

            elif agency == 'FDIC':
                staffers = defaultdict(int)
                for meeting in meetings:
                    for person in set(meeting.get('staff', [])):
                        staffers[person] += 1

                #staffers_by_agency.append((staffer, agency, count))

            elif agency == 'Federal Reserve':
                staffers = defaultdict(int)
                for meeting in meetings:
                    for participant_group in [x for x in meeting.get('participants', []) if x['organization'] == 'Federal Reserve Board']:
                        for person in set(participant_group.get('names', [])):
                            staffers[person] += 1

            elif agency == 'Treasury':
                staffers = defaultdict(int)
                for meeting in meetings:
                    for person in set(meeting.get('treasury_officials', [])):
                        staffers[person] += 1

            staffers_by_agency += [(x[0], agency, x[1], month_periods, x[1]/float(month_periods)) for x in staffers.items()]

        staffers_by_agency.sort(key=itemgetter(-1), reverse=True)

        for name, agency, count, months, avg in staffers_by_agency:
            if count > 1:
                writer.writerow([name, agency, str(count), str(months), str(avg), ])
