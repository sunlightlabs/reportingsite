# -*- coding: utf-8 -*-

import json
import re
import time

import requests
import lxml.html
from dateutil.parser import parse as dateparse
from django.utils.encoding import *
from pymongo import Connection

from scraper import Scraper


class CFTCScraper(Scraper):
    def __init__(self, *args, **kwargs):
        default_url = 'http://www.cftc.gov/LawRegulation/DoddFrankAct/ExternalMeetings/MeetingsAddedinLast7Days/index.htm'
        self.url = kwargs.get('url', default_url)
        self.agency = 'CFTC'


    def scrape(self):
        page = self.get_index()
        meeting_urls = self.parse_index(page)
        for url in meeting_urls:
            data = self.parse_meeting_page(url)
            self.save_data(data)
            time.sleep(.15)

    def get_index(self):
        return requests.get(self.url).content

    def parse_index(self, page):
        doc = lxml.html.fromstring(page)
        rows = doc.cssselect('div.row')
        for row in rows:
            url = row.cssselect('a')[0].attrib['href']
            yield ('http://www.cftc.gov/%s' % url).replace('../', '')

    def parse_meeting_page(self, url):
        page = requests.get(url).content
        doc = lxml.html.fromstring(page)

        m = re.search(r'(?P<date>\d\d?\/\d\d?\/\d{4}) (?P<time>\d\d?:\d\d (?:A|P)M)', doc.text_content())
        meeting_time = dateparse(' '.join(m.groups()))

        rows = doc.cssselect('div.row')
        rulemaking, cftc_staff, visitors, organizations = [self.data_from_row(row) for row in rows[:-1]]
        visitors = self.parse_visitors(visitors)
        organizations = self.parse_organizations(organizations)
        description = rows[-1].text_content().strip()
        return {'url': url,
                'rulemaking': rulemaking,
                'cftc_staff': cftc_staff,
                'visitors': visitors,
                'organizations': organizations,
                'description': description, 
                'meeting_time': meeting_time,
                }

    def parse_visitors(self, visitors):
        visitor_orgs = []
        for visitor in visitors:
            visitor = smart_str(visitor)
            regex = re.compile(r'\((?P<org>.*?)\)')
            m = regex.search(visitor)
            if m:
                name = regex.sub('', visitor).strip()
                org = m.groups('org')[0]
                visitor_orgs.append({'name': name, 'org': org, })
                continue

            regex = re.compile(r', (?P<org>.*)$')
            m = regex.search(visitor)
            if m:
                name = regex.sub('', visitor).strip()
                org = m.groups('org')[0]
                visitor_orgs.append({'name': name, 'org': org, })
                continue

            regex = re.compile(r' Staff$', re.I)
            m = regex.search(visitor)
            if m:
                org = regex.sub('', visitor).strip()
                visitor_orgs.append({'name': 'Staff', 'org': org, })
                continue

            regex = re.compile(r' – ')
            m = regex.search(visitor)
            if m:
                name, org = regex.split(visitor)
                visitor_orgs.append({'name': name.strip(), 'org': org.strip(), })
                continue

            regex = re.compile(r'-')
            m = regex.search(visitor)
            if m:
                try:
                    name, org = regex.split(visitor)
                except ValueError:
                    visitor_orgs.append({'name': visitor, 'org': None, })
                    continue
                visitor_orgs.append({'name': name.strip(), 'org': org.strip(), })
                continue

            visitor_orgs.append({'name': visitor, 'org': None, })

        if 'Staff' in [x['name'] for x in visitor_orgs]:
            org = [x['org'] for x in visitor_orgs if x['name'] == 'Staff'][0]
            name = [x['name'] for x in visitor_orgs if x['org'] == None][0]
            visitor_orgs = [{'name': name, 'org': org, }, ]

        return visitor_orgs

    def parse_organizations(self, organizations):
        organizations = [x for x in organizations if x.find('including:') == -1]
        return organizations


    def data_from_row(self, row):
        col = row.cssselect('div.column-coltwo')[0]
        return list(col.itertext())



if __name__ == '__main__':
    url = 'http://www.cftc.gov/LawRegulation/DoddFrankAct/ExternalMeetings/index.htm'
    scraper = CFTCScraper(url=url)
    scraper.scrape()
