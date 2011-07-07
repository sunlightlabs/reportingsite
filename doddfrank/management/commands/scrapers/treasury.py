import csv
import re
import sys
import urllib
import urllib2

import lxml.html
from pymongo import Connection
import requests
from dateutil.parser import parse as dateparse

from scraper import Scraper


class TreasuryScraper(Scraper):

    def __init__(self):
        self.agency = 'Treasury'

    def scrape(self):
        page = lxml.html.fromstring(sys.stdin.read())
        for data in self.parse_meeting_page(page):
            self.save_data(data)

    def parse_meeting_page(self, page):
        table = page.cssselect('table')[0]
        rows = table.cssselect('tr')
        for row in rows:
            datefield = row.cssselect('nobr')
            if not len(datefield):
                continue

            date = dateparse(datefield[0].text)

            tds = row.cssselect('td')
            if len(tds) != 4:
                continue

            rowdata = dict(zip(['treasury_officials', 'description', 'visitors'], row.cssselect('td')[1:]))

            for k, v in rowdata.iteritems():
                rowdata[k] = [lxml.html.fromstring(x).text_content().strip()
                                for x in
                                lxml.html.tostring(v).split('<br>')]

            visitor_orgs = []
            organizations = set([])
            for visitor in rowdata['visitors']:
                if ',' not in visitor:
                    visitor_orgs.append({'name': visitor, 'org': None, })
                    continue
                name, org = visitor.split(',', 1)
                visitor_orgs.append({'name': name.strip(), 'org': org.strip(), })
                organizations.add(org.strip())

            rowdata['visitors'] = visitor_orgs
            rowdata['meeting_time'] = date
            rowdata['organizations'] = sorted(list(organizations))

            yield rowdata


    '''
    def list_urls(self):
        url = 'http://www.treasury.gov/initiatives/wsr/Pages/transparency.aspx'
        page = urllib2.urlopen(url).read()
        for url in set(re.findall(r'"(\/initiatives\/wsr\/Pages\/.*?)"', page)):
            if url.endswith('wall-street-reform.aspx') or url.endswith('Transparency.aspx'):
                continue
            yield 'http://www.treasury.gov' + url

    def scrape(self):
        for url in self.list_urls():
            self.parse_page(url)

    def parse_page(self, url):
        r = urllib2.urlopen(url)
        page = r.read()
        inputs = re.findall(r'<input .*?>', page)
        params = {}
        for input in inputs:
            k = re.search(r'id=(?:"|\')(.*?)(?:"|\')', input).groups()[0]
            v = re.search(r'value=(?:"|\')(.*?)(?:"|\')', input)
            if v:
                v = v.groups()[0]
            else:
                v = None
            params[k] = v

        m = re.search(r"__doPostBack\('([a-z0-9\$_]+)','(dvt_firstrow=.*Paged=TRUE.*?)'", page)
        if not m:
            return
        params['__EVENTTARGET'], params['__EVENTARGUMENT'] = m.groups()
        target = m.groups()[0]
        params['ctl00$ScriptManager'] = '$'.join(target.split('$')[:-1]) + '$updatePanel' + target.replace('$', '_', 2).split('$')[0] + '|' + target
        request = urllib2.Request(url, data=urllib.urlencode(params))
        r = urllib2.urlopen(request)
        print r.read()
        return
    '''


if __name__ == '__main__':
    scraper = TreasuryScraper()
    scraper.scrape()
