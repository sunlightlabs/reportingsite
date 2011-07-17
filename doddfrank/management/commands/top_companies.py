from collections import defaultdict
from operator import itemgetter
import sys

from pymongo import Connection

from django.core.management.base import BaseCommand, CommandError

from doddfrank.views import UnicodeWriter


class Command(BaseCommand):

    def handle(self, *args, **options):
        collection = Connection().test.meetings

        companies = defaultdict(int)

        for meeting in collection.find():
            for org in set(meeting.get('organizations', [])):
                companies[org] += 1

        writer = UnicodeWriter(sys.stdout)
        writer.writerow(('organization','meetings'))
        for company, count in sorted(companies.items(), key=itemgetter(1), reverse=True):
            writer.writerow((company, str(count)))
