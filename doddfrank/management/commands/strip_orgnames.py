from pymongo import Connection

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        collection = Connection().test.meetings

        for meeting in collection.find():
            if meeting.get('organizations'):
                meeting['organizations'] = [x.strip() for x in meeting.get('organizations', []) if x is not None]
                if len(meeting['organizations']) == 0:
                    del(meeting['organizations'])

            visitors = meeting.get('visitors', [])
            if visitors is not None:
                for visitor in visitors:
                    if visitor is None:
                        continue
                    try:
                        if visitor['org']:
                            visitor['org'] = visitor['org'].strip()
                        meeting['visitors'] = visitors
                    except TypeError:
                        pass

            collection.update({'_id': meeting['_id']}, meeting)

