import codecs
import csv
import sys

from pymongo import Connection

from django.core.management.base import BaseCommand, CommandError


# From http://docs.python.org/library/csv.html
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self



class Command(BaseCommand):

    def handle(self, *args, **options):
        collection = Connection().test.meetings

        reader = UnicodeReader(sys.stdin)
        reader.next()
        for row in reader:
            print row
            try:
                old, new = row
            except ValueError:
                old = row[0]
                new = ''

            meetings = collection.find({'organizations': old})
            for meeting in meetings:
                orgs = meeting['organizations']
                del(orgs[orgs.index(old)])
                if new:
                    orgs.append(new)
                orgs.sort()
                collection.update({'_id': meeting['_id']}, meeting)

            meetings = collection.find({'visitors.org': old})
            for meeting in meetings:
                visitors = meeting['visitors']
                for visitor in visitors:
                    if visitor['org'] == old:
                        visitor['org'] = new
                meeting['visitors'] = visitors
                collection.update({'_id': meeting['_id']}, meeting)
