# Taken from here:
# http://stackoverflow.com/questions/1846135/python-csv-library-with-unicode-utf-8-support-that-just-works

import csv

class UnicodeCsvReader(object):
    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_reader = csv.reader(f, **kwargs)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        # read and split the csv row into fields
        row = self.csv_reader.next() 
        # now decode
        return [unicode(cell, self.encoding) for cell in row]

    @property
    def line_num(self):
        return self.csv_reader.line_num


class UnicodeCsvWriter(object):
    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_writer = csv.writer(f, **kwargs)
        self.encoding = encoding

    def writerow(self, row):
        return self.csv_writer.writerow([c.encode(self.encoding) for c in row])

