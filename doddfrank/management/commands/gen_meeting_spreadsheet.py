from __future__ import print_function

import sys

from django.core.management.base import BaseCommand
from optparse import make_option

from unicodecsv import UnicodeCsvWriter
from doddfrank.models import Meeting


class Command(BaseCommand):
    args = ''
    help = 'Exports a CSV to stdout listing each meeting.'
    option_list = BaseCommand.option_list + (
        make_option('--agency', action='store', dest='agency', metavar='AGENCY',
                    default=None, help='Limit the queries to this agency.'),
    )

    def handle(self, *args, **options):
        print(u'Fetching meetings.',
              file=sys.stderr)

        meetings = Meeting.objects.all()
        agency = options.get('agency')
        if agency is not None:
            meetings = meetings.filter(agency__initials=agency)

        print(u'Writing CSV.',
              file=sys.stderr)
        writer = UnicodeCsvWriter(sys.stdout)

        header_row = [u'Meeting Hash',
                      u'Agency',
                      u'Date',
                      u'Topic',
                      u'Communication Type',
                      u'Description'
                     ]
        writer.writerow(header_row)

        for mtg in meetings:
            writer.writerow([mtg.import_hash,
                             mtg.agency.slug,
                             mtg.date.strftime('%Y-%m-%d'),
                             mtg.topic or mtg.subcategory or mtg.category,
                             mtg.communication_type,
                             mtg.description])




