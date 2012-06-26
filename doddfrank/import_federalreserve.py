import dateutil.parser

from doddfrank.importlib import (slurp_data, agency_or_die,
                                 reconcile_database, import_meetings,
                                 import_attendees, prune_attendees)
from doddfrank.models import Agency, Attendee, Organization, Meeting


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankfed&query=select%20*%20from%20%60MeetingTable1%60'
SCRAPER_ATTENDEES_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankfed&query=select%20*%20from%20%60AttendeeTable1%60'


TheFed = agency_or_die('Fed')


def print_object_counts():
    print 'Object counts:'
    print '  Agency: {0}'.format(Agency.objects.count())
    print '  Organization: {0}'.format(Organization.objects.count())
    print '  Meeting: {0}'.format(Meeting.objects.count())
    print '  Attendee: {0}'.format(Attendee.objects.count())


def meeting_keyfunc(record, record_hash):
    return {
        'agency': TheFed,
        'date': dateutil.parser.parse(record['date']).date(),
        'import_hash': record_hash
    }


def meeting_copyfunc(record, meeting):
    meeting.communication_type = record['type']
    meeting.description = record['summary'] or ''
    meeting.category = record['category']
    meeting.subcategory = record['subcategory']
    meeting.topic = ''
    meeting.attendee_hash = ''
    meeting.source_url = record['link']


def attendee_keyfunc(record, record_hash):
    return {
        'name': record['attendee_name']
    }


def attendee_copyfunc(record, attendee):
    attendee.name = record['attendee_name']


SharedKeys = ['date', 'name', 'category']


def main():
    print_object_counts()

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc)


    print 'Importing attendees'
    attendees = slurp_data(SCRAPER_ATTENDEES_URL)
    import_attendees(meetings, attendees, SharedKeys,
                     attendee_keyfunc, attendee_copyfunc,
                     meeting_keyfunc, meeting_copyfunc,
                     'affiliation')

    meeting_objects = Meeting.objects.filter(agency=TheFed)
    reconcile_database(meeting_objects, meetings)

    prune_attendees()

    print 'Done'

    print_object_counts()

    
if __name__ == "__main__":
    main()


