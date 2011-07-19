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
        writer.writerow(('agency','meetings'))

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
            #print agency, start, end, month_periods
            #print agency, meetings.count(), 

            meetings_per_month = meetings.count() / float(month_periods)
            writer.writerow((agency, str(meetings_per_month)))
