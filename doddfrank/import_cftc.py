import dateutil.parser

from doddfrank.importlib import (slurp_data, agency_or_die,
                                 reconcile_database, import_meetings,
                                 import_attendees, prune_attendees, prune_organizations,
                                 ObjectCounts)
from doddfrank.models import Agency, Attendee, Organization, Meeting


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankcftc&query=select%20*%20from%20%60meetings%60'
SCRAPER_ATTENDEES_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankcftc&query=select%20*%20from%20%60attendees%60'


CFTC = agency_or_die('CFTC')


def meeting_keyfunc(record, record_hash):
    return {
        'agency': CFTC,
        'date': dateutil.parser.parse(record['meeting_time']).date(),
        'import_hash': record_hash
    }


def meeting_copyfunc(record, meeting):
    meeting.communication_type = 'Meeting'
    meeting.description = record['description']
    meeting.category = ''
    meeting.subcategory = ''
    meeting.topic = record['topic']
    meeting.attendee_hash = ''
    meeting.source_url = record['url']


def attendee_keyfunc(record, record_hash):
    return {
        'name': record['attendee_name'].strip()
    }

def attendee_copyfunc(record, attendee):
    attendee.name = record['attendee_name'].strip()


SharedKeys = ['meeting_time', 'description', 'topic', 'url']


def main():
    obj_counts = ObjectCounts(CFTC)
    print unicode(obj_counts)

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc)

    print 'Importing attendees'
    attendees = slurp_data(SCRAPER_ATTENDEES_URL)
    import_attendees(meetings, attendees, SharedKeys,
                     attendee_keyfunc, attendee_copyfunc,
                     meeting_keyfunc, meeting_copyfunc,
                     'attendee_org')

    print 'Reconciling database'
    meeting_objects = Meeting.objects.filter(agency=CFTC)
    reconcile_database(meeting_objects, meetings)

    prune_attendees()
    prune_organizations()

    print obj_counts.update().diffstat()
    print 'Done'

    
if __name__ == "__main__":
    main()



