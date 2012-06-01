import sys
import progressbar

import dateutil.parser

from doddfrank.importlib import (slurp_data, agency_or_die,
                                 dict_hash, DictSlicer, index_dict_list,
                                 reconcile_database, import_meetings,
                                 prune_attendees)
from doddfrank.models import Agency, Attendee, Organization, Meeting


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankctfcmeetings&query=select%20*%20from%20%60meetings%60'
SCRAPER_ATTENDEES_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankctfcmeetings&query=select%20*%20from%20%60attendees%60'


CFTC = agency_or_die('CFTC')


def print_object_counts():
    print 'Object counts:'
    print '  Agency: {0}'.format(Agency.objects.count())
    print '  Organization: {0}'.format(Organization.objects.count())
    print '  Meeting: {0}'.format(Meeting.objects.count())
    print '  Attendee: {0}'.format(Attendee.objects.count())


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


SharedKeys = ['meeting_time', 'description', 'topic', 'url']


def main():
    print_object_counts()

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    meeting_index = index_dict_list(meetings, SharedKeys)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc)

    meeting_objects = Meeting.objects.filter(agency=CFTC)
    reconcile_database(meeting_objects, meetings)

    prune_attendees()

    print 'Done'

    print_object_counts()

    
if __name__ == "__main__":
    main()



