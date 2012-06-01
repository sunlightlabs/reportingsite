import sys
import progressbar

import dateutil.parser

from doddfrank.importlib import (slurp_data, agency_or_die,
                                 reconcile_database, import_meetings,
                                 import_attendees, prune_attendees)
from doddfrank.models import Agency, Attendee, Organization, Meeting


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=fed_meeting_log_v3&query=select%20*%20from%20%60MeetingTable1%60'
SCRAPER_ATTENDEES_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=fed_meeting_log_v3&query=select%20*%20from%20%60AttendeeTable1%60'


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
    org = None
    if record['affiliation']:
        org = Organization.objects.get(name=record['affiliation'])
    return {
        'name': record['attendee_name'],
        'org': org
    }


def attendee_copyfunc(record, attendee):
    attendee.name = record['attendee_name']
    attendee.org = record['affiliation']


SharedKeys = ['date', 'name', 'category']


def main():
    print_object_counts()

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc)

    meeting_objects = Meeting.objects.filter(agency=TheFed)
    reconcile_database(meeting_objects, meetings)

    print 'Importing attendees'
    attendees = slurp_data(SCRAPER_ATTENDEES_URL)
    import_attendees(meetings, attendees, SharedKeys,
                     attendee_keyfunc, attendee_copyfunc,
                     meeting_keyfunc, meeting_copyfunc,
                     'org')

    prune_attendees()

    print 'Done'

    print_object_counts()

    
if __name__ == "__main__":
    main()


