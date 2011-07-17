import csv
import re
import urllib2

from dateutil.parser import parse as dateparse
from pymongo import Connection

from scraper import Scraper


class FDICScraper(Scraper):

    def __init__(self):
        self.url = 'http://www.fdic.gov/regulations/meetings/vlog.csv'
        self.agency = 'FDIC'

    def scrape(self):
        reader = csv.DictReader(urllib2.urlopen(self.url))
        for row in reader:
            data = {'staff': self.parse_staff(row['Person Visited']),
                    'meeting_time': dateparse(row['Date']),
                    'organizations': self.parse_organizations(row['Affiliation']),
                    'visitors': self.parse_visitors(row['Visitor']),
                    'material_provided': row['Material <br />Provided'],
                    'description': row['Issues Discussed'].replace(':', '; '),
                    }
            self.save_data(data)

    def parse_staff(self, staff):
        return [x.strip() for x in staff.split(':')]

    def parse_visitors(self, visitors):
        visitors = [x.strip() for x in visitors.split(':')
                        if x != 'Multiple, Visitors'
                        and x != 'Multiple , Visitors']
        visitor_orgs = []
        for visitor in visitors:
            regex = re.compile(r'\((?P<org>.*?)\)')
            m = regex.search(visitor)
            if m:
                name = regex.sub('', visitor).strip()
                org = m.groups('org')[0]
                visitor_orgs.append({'name': name, 'org': org, })
            else:
                visitor_orgs.append({'name': visitor, 'org': None, })
        return visitor_orgs

    def parse_organizations(self, organizations):
        organizations = re.sub(r', Inc', ' Inc', organizations)
        organizations = re.split(r'(?:;|,)', organizations)
        return [x.strip() for x in organizations]

if __name__ == '__main__':
    scraper = FDICParser()
    scraper.scrape()
