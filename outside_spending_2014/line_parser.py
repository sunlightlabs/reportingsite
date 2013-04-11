""" Parse a line from an FEC file based on the NYT's FECH utility's file definition csvs, available here: https://github.com/NYTimes/Fech/tree/master/sources"""

import csv
import re

# where is the sources directory located ?
from read_FEC_settings import CSV_FILE_DIRECTORY


class line_parser(object):

    def __init__(self, form):
        self.form = form
        self.regex_dict = {}
        self.column_locations_dict = {}

        form_file = "%s/%s.csv" % (CSV_FILE_DIRECTORY, form)
        # Need to open in universal newline mode
        form_reader = csv.reader(open(form_file, 'rU'))
        header = form_reader.next()

        for i, regex in enumerate(header):
            if (regex != '' and regex != 'canonical'):
                self.regex_dict[regex] = i

        #print self.regex_dict

        # read in the body rows
        body_rows = []
        for row in form_reader:
            body_rows.append(row)

        # Now create the column locations dict for each version
        for regex in self.regex_dict:
            this_column_locations = {}
            for row in body_rows:
                # the csv files sometimes are missing trailing commas when values are absent.
                if (len(row) > self.regex_dict[regex]):
                    if (row[self.regex_dict[regex]] != ''):
                        # The csv files use 1-indexed positions - subtract 1 because
                        #  we want them 0-indexed.
                        this_column_locations[row[0]] = int(row[self.regex_dict[regex]]) - 1
            self.column_locations_dict[regex] = this_column_locations
        #print regex, this_column_locations

    def get_column_locations(self, version):
        """Just return the raw column locations hash--I mean dict"""
        return self.column_locations_dict

    def parse_line(self, line_array, version):
        """ Return a dict of all variables"""
        found_version = False
        regex_key = None
        # make sure we have this version; since these regexes are non-overlapping, we don't care about the order, and can iterate over the hash keys (instead of an ordered array)
        for regex in self.regex_dict:
            if (re.match(regex, version)):
                regex_key = regex
                found_version = True

        if not found_version:
            raise Exception("Can't find data to parse line type=%s version=%s" % (self.form_type, version))

        line_dict = {}
        for column in self.column_locations_dict[regex_key]:
            col_position = self.column_locations_dict[regex_key][column]
            #print "PARSER: %s version: %s, line: %s len: %s" % (column, version, col_position, len(line_array))
            # sometimes trailing commas are omitted, so test that there actually is a value
            if (col_position <= len(line_array) - 1):
                line_dict[column] = line_array[col_position]
            else:
                line_dict[column] = ''
        return line_dict
