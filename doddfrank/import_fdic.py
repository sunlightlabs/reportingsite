import sys
import progressbar
import dateutil.parser

from doddfrank.importlib import (slurp_data, agency_or_die,
                                 reconcile_database, import_meetings,
                                 prune_attendees)
from doddfrank.models import Agency, Attendee, Organization, Meeting


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankfdicmeetings&query=select%20*%20from%20%60meetings%60'
SCRAPER_ATTENDEES_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfrankfdicmeetings&query=select%20*%20from%20%60meetings%60'

FDIC = agency_or_die('FDIC')


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
        'agency': FDIC
    }


def meeting_copyfunc(record, meeting):
    meeting.communication_type = 'Meeting'
    meeting.date = dateutil.parser.parse(record['Date']).date()
    meeting.category = ''
    meeting.subcategory = ''
    meeting.topic = record['Topics']
    meeting.source_url = 'http://www.fdic.gov/regulations/meetings/'


def main():
    print_object_counts()

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc)

    meeting_objects = Meeting.objects.filter(agency=FDIC)
    reconcile_database(meeting_objects, meetings)

    print 'Importing attendees'
    attendees = slurp_data(SCRAPER_ATTENDEES_URL)
    progress = progressbar.ProgressBar()

    for a in progress(attendees):
        a_date = dateutil.parser.parse(a['Date']).date()
        try:
            meeting = Meeting.objects.get(agency=FDIC,
                                          date=a_date,
                                          topic=a['Topics'],
                                          attendee_hash=a['AttendeeHash'])
        except Meeting.DoesNotExist:
            print 'No such meeting found for attendee record ({0})'.format(a)
            continue
        except Meeting.MultipleObjectsReturned:
            print 'Database integrity failed: multiple meetings for attendee record ({0})'.format(a)
            continue

        if a['Org']:
            (organization, created) = Organization.objects.get_or_create(name=a['Org'])
            if created:
                organization.save()
        else:
            organization = None

        (attendee, created) = Attendee.objects.get_or_create(name=a['Attendee'],
                                                             org=organization)
        if created:
            meeting.attendees.add(attendee)
            attendee.save()


    prune_attendees()

    print 'Done'

    print_object_counts()

    
if __name__ == "__main__":
    main()

