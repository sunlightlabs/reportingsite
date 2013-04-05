import sys
import progressbar

import dateutil.parser
from argparse import ArgumentParser

from doddfrank.importlib import (slurp_data, agency_or_die,
                                 reconcile_database, import_meetings,
                                 import_organizations, prune_organizations,
                                 ObjectCounts)
from doddfrank.models import Agency, Attendee, Organization, Meeting


parser = ArgumentParser()
parser.add_argument('--update-existing', '-u', default=False, action='store_true', help='Updates database objects even if the key fields have not changed.')
args = parser.parse_args()


SCRAPER_MEETINGS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfranksec&query=select%20*%20from%20%60meetings%60'
SCRAPER_ORGANIZATIONS_URL = 'https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=jsondict&name=doddfranksec&query=select%20*%20from%20%60organizations%60'


SEC = agency_or_die('SEC')

SharedKeys = [
    'pdf_url'
]


def meeting_keyfunc(record, record_hash):
    return {
        'agency': SEC,
        'date': dateutil.parser.parse(record['meeting_time']).date(),
        'import_hash': record_hash
    }


def meeting_copyfunc(record, meeting):
    meeting.communication_type = record['type']
    meeting.description = record['description'] or ''
    meeting.category = record['category']
    meeting.subcategory = ''
    meeting.topic = ''
    meeting.attendee_hash = ''
    meeting.source_url = record['url']



def main():
    obj_counts = ObjectCounts(SEC)
    print unicode(obj_counts)

    print 'Importing meetings'
    meetings = slurp_data(SCRAPER_MEETINGS_URL)
    import_meetings(meetings, meeting_keyfunc, meeting_copyfunc,
                    update_existing=args.update_existing)

    print 'Importing organizations'
    organizations = slurp_data(SCRAPER_ORGANIZATIONS_URL)
    import_organizations(meetings, organizations, SharedKeys,
                         'org_name', meeting_keyfunc)

    meeting_objects = Meeting.objects.filter(agency=SEC)
    #reconcile_database(meeting_objects, meetings)

    #prune_organizations()

    print obj_counts.update().diffstat()
    print 'Done'

    
if __name__ == "__main__":
    main()



