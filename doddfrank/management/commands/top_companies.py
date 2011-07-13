from collections import defaultdict
from operator import itemgetter

from pymongo import Connection

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        collection = Connection().test.meetings

        companies = defaultdict(int)

        for meeting in collection.find():
            if meeting.has_key('type') and meeting.get('type') != 'Meeting':
                continue
            for org in meeting.get('organizations', []):
                companies[org] += 1

        for company, count in sorted(companies.items(), key=itemgetter(1), reverse=True):
            print company, count
