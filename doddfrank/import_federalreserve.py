import sys
import progressbar

import dateutil.parser

from doddfrank.importlib import (slurp_data, dict_hash, DictSlicer, index_dict_list,
                                 reconcile_database, import_meetings,
                                 prune_attendees)
from doddfrank.models import Agency, Attendee, Organization, Meeting


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=fed_meeting_log_v3&query=select%20*%20from%20%60MeetingTable1%60'
SCRAPER_ATTENDEES_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=fed_meeting_log_v3&query=select%20*%20from%20%60AttendeeTable1%60'

try:
    TheFed = Agency.objects.get(initials='Fed')
except Agency.DoesNotExist:
    print >>sys.stderr, 'Fed is not a registered agency.'
    sys.exit(1)

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


SharedKeys = ['date', 'name', 'category']


def main():
    print_object_counts()

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    meeting_index = index_dict_list(meetings, SharedKeys)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc)

    meeting_objects = Meeting.objects.filter(agency=TheFed)
    reconcile_database(meeting_objects, meetings)

    print 'Importing attendees'
    attendees = slurp_data(SCRAPER_ATTENDEES_URL)
    progress = progressbar.ProgressBar(maxval=len(attendees))
    for a in progress(attendees):
        m_keys = DictSlicer(*SharedKeys)(a)
        m_hash = dict_hash(m_keys)
        m = meeting_index[m_hash]
        a_date = dateutil.parser.parse(a['date'])

        m_keys = meeting_keyfunc(m, dict_hash(m))
        meeting = Meeting.objects.get(**m_keys)

        if a['affiliation']:
            (organization, created) = Organization.objects.get_or_create(name=a['affiliation'])
            if created:
                organization.save()
                meeting.organizations.add(organization)
                meeting.save()

        if a['attendee_name']:
            (attendee, created) = Attendee.objects.get_or_create(name=a['attendee_name'],
                                                                 org=organization)
            if created:
                attendee.save()
                meeting.attendees.add(attendee)
                meeting.save()

    prune_attendees()

    print 'Done'

    print_object_counts()

    
if __name__ == "__main__":
    main()


