import sys
import progressbar
import dateutil.parser

from doddfrank.importlib import (dict_hash, slurp_data, 
                                 reconcile_database, import_meetings,
                                 import_attendees, prune_attendees, prune_organizations)
from doddfrank.models import Agency, Attendee, Organization, Meeting


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfranktreasury&query=select%20*%20from%20%60meetings%60'
SCRAPER_ATTENDEES_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfranktreasury&query=select%20*%20from%20%60attendees%60'


try:
    Treasury = Agency.objects.get(initials='Treasury')
except Agency.DoesNotExist:
    print >>sys.stderr, 'Treasury is not a registered agency.'
    sys.exit(1)


def print_object_counts():
    print 'Object counts:'
    print '  Agency: {0}'.format(Agency.objects.count())
    print '  Organization: {0}'.format(Organization.objects.count())
    print '  Meeting: {0}'.format(Meeting.objects.count())
    print '  Attendee: {0}'.format(Attendee.objects.count())


def meeting_keyfunc(record, record_hash):
    return {
        'date': dateutil.parser.parse(record['Date']).date(),
        'import_hash': record_hash,
        'agency': Treasury
    }


def meeting_copyfunc(record, meeting):
    meeting.communication_type = 'Meeting'
    meeting.date = dateutil.parser.parse(record['Date']).date()
    meeting.category = ''
    meeting.subcategory = ''
    meeting.topic = record['Topics']
    meeting.attendee_hash = record['AttendeeHash']
    meeting.source_url = record['Url']


def attendee_keyfunc(record, record_hash):
    return {
        'name': record['Attendee']
    }


def attendee_copyfunc(record, attendee):
    attendee.name = record['Attendee']


SharedKeys = ['Topics', 'MonthName', 'Year', 'Date', 'AttendeeHash']


def main():
    (treasury, created) = Agency.objects.get_or_create(initials='Treasury')
    if created:
        treasury.name = 'Treasury'
        treasury.meeting_list_url = 'http://www.treasury.gov/initiatives/wsr/Pages/transparency.aspx'
        treasury.save()

    print_object_counts()

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc)

    print 'Importing attendees'
    attendees = slurp_data(SCRAPER_ATTENDEES_URL)
    import_attendees(meetings, attendees, SharedKeys,
                     attendee_keyfunc, attendee_copyfunc,
                     meeting_keyfunc, meeting_copyfunc,
                     'Org')

    meeting_objects = Meeting.objects.filter(agency=treasury)
    reconcile_database(meeting_objects, meetings)

    prune_attendees()
    prune_organizations()

    print 'Done'

    print_object_counts()

    
if __name__ == "__main__":
    main()

