import dateutil.parser

from doddfrank.importlib import (slurp_data, agency_or_die,
                                 reconcile_database, import_meetings,
                                 import_attendees, prune_attendees, prune_organizations,
                                 ObjectCounts)
from doddfrank.models import Agency, Attendee, Organization, Meeting


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankfdic&query=select%20*%20from%20%60meetings%60'
SCRAPER_ATTENDEES_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankfdic&query=select%20*%20from%20%60attendees%60'


FDIC = agency_or_die('FDIC')


def meeting_keyfunc(record, record_hash):
    return {
        'date': dateutil.parser.parse(record['Date']).date(),
        'import_hash': record_hash,
        'agency': FDIC
    }


def meeting_copyfunc(record, meeting):
    meeting.communication_type = 'Meeting'
    meeting.date = dateutil.parser.parse(record['Date']).date()
    meeting.category = ''
    meeting.subcategory = ''
    meeting.topic = record['Topics']
    meeting.source_url = 'http://www.fdic.gov/regulations/meetings/'


def attendee_keyfunc(record, record_hash):
    return {
        'name': record['Attendee']
    }


def attendee_copyfunc(record, attendee):
    attendee.name = record['Attendee']


SharedKeys = ['Date', 'Topics', 'Disclosed']


def main():
    obj_counts = ObjectCounts(FDIC)
    print unicode(obj_counts)

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc)

    print 'Importing attendees'
    attendees = slurp_data(SCRAPER_ATTENDEES_URL)
    import_attendees(meetings, attendees, SharedKeys,
                     attendee_keyfunc, attendee_copyfunc,
                     meeting_keyfunc, meeting_copyfunc,
                     'Org')

    print 'Reconciling database'
    meeting_objects = Meeting.objects.filter(agency=FDIC)
    reconcile_database(meeting_objects, meetings)

    prune_attendees()
    prune_organizations()

    print obj_counts.update().diffstat()
    print 'Done'

    
if __name__ == "__main__":
    main()

