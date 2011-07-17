from pymongo import Connection

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        collection = Connection().test.meetings

        for meeting in collection.find({'organizations': {'$regex': u'\xe2\x80\x99'}}):
            meeting['organizations'] = [x.replace(u'\xe2\x80\x99', "'") for x in meeting.get('organizations', []) if x is not None]
            if len(meeting['organizations']) == 0:
                del(meeting['organizations'])

            visitors = meeting.get('visitors', [])
            if visitors is not None:
                for visitor in visitors:
                    visitor['name'] = visitor['name'].replace(u'\xe2\x80\x99', "'")
                meeting['visitors'] = visitors

            collection.update({'_id': meeting['_id']}, meeting)
            print meeting['_id']
