import sys

from itertools import chain
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from progressbar import ProgressBar, Counter, Timer, ETA

from jellyfish import jaro_winkler
from unicodecsv import UnicodeCsvReader, UnicodeCsvWriter
from doddfrank.models import Organization, OrganizationNameCorrection
from doddfrank.importlib import (prune_organizations, prune_attendees,
                                 standardized_organization_name)


def export_current_corrections():
    print >>sys.stderr, u'Exporting spreadsheet of existing corrections.'
    sys.stderr.flush()
    suggestion_writer = UnicodeCsvWriter(sys.stdout)
    for correction in OrganizationNameCorrection.objects.all():
        suggestion_writer.writerow([correction.original, correction.replacement])


def export_standardized_suggestions():
    org_names = [o.name for o in Organization.objects.all()]
    combination_count = len(org_names) * (len(org_names) - 1)
    print >>sys.stderr, "Considering {0} names, {1} combinations.".format(len(org_names), combination_count)
    sys.stderr.flush()

    progress = ProgressBar(maxval=combination_count, widgets=[Counter(), '/', str(combination_count), ' ', Timer(), ' ', ETA()])

    matches = [
        (a, b, fixed_a)
        for (a, b, fixed_a, fixed_b) in progress(((a, b,
                                                   standardized_organization_name(a),
                                                   standardized_organization_name(b))
                                                  for (i, a) in enumerate(org_names)
                                                  for (j, b) in enumerate(org_names)
                                                  if j > i
                                                  and a != b))
        if fixed_a == fixed_b
    ]

    if len(matches) > 0:
        print >>sys.stderr, "Found {0} matches.".format(len(matches))
        sys.stderr.flush()
        suggestion_writer = UnicodeCsvWriter(sys.stdout)
        for match in matches:
            if match[0] != match[2]:
                suggestion_writer.writerow([match[0], match[2]])
            if match[1] != match[2]:
                suggestion_writer.writerow([match[1], match[2]])


def export_jarowinkler_suggestions():
    org_names = [o.name for o in Organization.objects.all()]
    matches = [
        (a, b, score)
        for (a, b, score) in ((a, b, jaro_winkler(a.encode('utf-8'), b.encode('utf-8')))
                              for (i, a) in enumerate(org_names)
                              for (j, b) in enumerate(org_names)
                              if j > i
                              and a != b
                              and len(a) > 3
                              and len(b) > 3)
        if score > 0.95]

    print >>sys.stderr, "Found {0} matches.".format(len(matches))
    if len(matches) == 0:
        return

    #matched_names = list(chain((a for (a, b, score) in matches),
    #                           (b for (a, b, score) in matches)))

    #name_freq = freq(matched_names)
    #pprint(name_freq, stream=sys.stderr)

    sys.stderr.flush()
    suggestion_writer = UnicodeCsvWriter(sys.stdout)
    for (a, b, score) in matches:
        a_chars = set(a)
        b_chars = set(b)
        original = a if len(a_chars) > len(b_chars) else b
        replacement = b if len(a_chars) > len(b_chars) else a
        suggestion_writer.writerow([original, replacement])


def freq(l):
    d = {}
    for x in l:
        n = d.get(x, 0)
        d[x] = n + 1
    return d


def import_corrections():
    correction_records = UnicodeCsvReader(sys.stdin)
    for (line_number, record) in enumerate(correction_records, start=1):
        if len(record) == 2:
            if record[0] == record[1]:
                print >>sys.stderr, "Suggested correction matches itself."
            else:
                # If there is a correction X=>Y then we do not want to 
                # create a correction Y=>Z because that should be a correction
                # X=>Z but that may be dangerous.
                existing = OrganizationNameCorrection.objects.filter(original=record[1])
                if existing:
                    continue

                (correction, created) = OrganizationNameCorrection.objects.get_or_create(
                    original=record[0],
                    replacement=record[1])
                if created:
                    print u"{0!s: <40} => {1}".format(record[0], record[1])
                else:
                    print >>sys.stderr, u"Replacement alread exists: {0} => {1}".format(record[0], record[1])
                correction.save()
        else:
            print >>sys.stderr, "Invalid record in input on line {0}".format(line_number)

    prune_attendees()
    prune_organizations()


class Command(BaseCommand):
    args = '<command>'
    help = 'Exports a list of suggested corrections to stdout or imports a list of corrections (same format) from stdin.'
    option_list = BaseCommand.option_list + (
        make_option('--method',
                    action='store',
                    dest='method',
                    default='standardize',
                    metavar='<standardize|jarowinkler>',
                    help='The method to use for comparing org. names'),
    )

    def handle(self, command, *args, **options):
        if command == "import":
            import_corrections()
        elif command == "export":
            if options['method'] == "jarowinkler":
                export_jarowinkler_suggestions()
            elif options['method'] == "standardize":
                export_standardized_suggestions()
            else:
                raise CommandError("Unrecognized comparison option: {0}".format(options['method']))
        elif command == "current":
            export_current_corrections()
        else:
            raise CommandError("Unrecognized command: {0}".format(command))

