from cStringIO import StringIO
import re
import sys

from dateutil.parser import parse as dateparse
import lxml.html
import requests

import warnings
warnings.simplefilter("ignore")
import pyPdf
from pymongo import Connection

from scraper import Scraper


class FedreserveScraper(Scraper):

    pages = ['reform_systemic.htm',
             'reform_derivatives.htm',
             'reform_interchange.htm',
             'reform_payments.htm',
             'reform_consumer.htm',
             'reform_resolution.htm', ]

    def __init__(self):
        self.agency = 'Federal Reserve'

    def scrape(self):
        url = 'http://www.federalreserve.gov/newsevents/%s'
        for pagename in self.pages:
            page = requests.get(url % pagename).content
            doc = lxml.html.fromstring(page)
            for data in self.parse_page(doc):
                self.save_data(data)

    def parse_page(self, doc):
        category = re.sub(r'^[IV]+\. ', '', doc.cssselect('h4')[0].text_content().strip())
        table = doc.cssselect('table.earegulate')[0]
        for row in table.cssselect('tr')[1:]:
            cells = row.cssselect('td')
            try:
                pdf_url = cells[0].cssselect('a')[0].attrib['href']
            except IndexError:
                continue
            self.pdf_url = 'http://www.federalreserve.gov%s' % pdf_url

            date = dateparse(cells[1].text_content().strip())
            typeof = cells[2].text_content().strip()
            if typeof != 'Letter':
                pdf_data = self.parse_pdf() #self.pdf_url)
            else:
                pdf_data = {}

            if pdf_data is None:
                continue
            
            data = pdf_data
            data.update({'meeting_time': date,
                         'type': typeof,
                         'url': self.pdf_url,
                         })
            yield data


    def save_pdf(self, url, content):
        filename = 'pdfs/' + self.pdf_url.split('/')[-1]
        with open(filename, 'wb') as fh:
            fh.write(content)

    def parse_pdf(self):
        content = requests.get(self.pdf_url).content

        #self.save_pdf(self.pdf_url, content)

        try:
            pdf = pyPdf.PdfFileReader(StringIO(content))
        except pyPdf.utils.PdfReadError:
            print 'unable to open', self.pdf_url
            return None

        item = {'pdf_url': self.pdf_url, }

        first_page = pdf.getPage(0).extractText().strip()
        summary = re.search(r'Summary:(.*)', first_page)
        try:
            summary = summary.groups()[0].strip()
        except AttributeError:
            summary = None

        item['summary'] = summary

        title = re.search(r'^(.*?)(?:Participants|Board members|Presenters):', first_page, re.S)
        if not title:
            return None

        title = title.groups()[0].strip()

        # Remove date from title
        item['title'] = re.sub(r'\b[A-Z][a-z]+\s\d\d?,\s\d{4}', '', title).strip()

        all_participants = self.parse_participants(first_page)

        item['participants'] = []
        item['organizations'] = set([])

        for category, participants in all_participants:
            participants = NameExtractor(participants.strip()).extract()
            for org, names in participants:
                item['participants'].append({'category': category,
                                             'organization': org,
                                             'names': names, })
                item['organizations'].add(org)

        item['organizations'] = sorted(list(item['organizations']))

        return item


    def parse_participants(self, text):
        return re.findall(r'(Participants|Board members|Council members|Presenters):(.*?)(?:Summary|\n)', text, re.S)
        if not m:
            return None
        return m.groups()[0]


class NameExtractor(object):

    def __init__(self, s):
        self.s = s

    def extract(self):
        parts = re.split(r'\((.*?)\)', self.s)
        zipped = []
        if len(parts) == 1:
            org = None
            names = self.splitnames(parts[0])
            zipped.append((org, names))
        else:
            for names, org in zip(parts[::2], parts[1::2]):
                org = org.strip()
                names = self.splitnames(names)
                zipped.append((org, names))

        return zipped

    def splitnames(self, names):
        names = re.split(r'(?:,|and)', names)
        names = [x.strip(';').strip() for x in names]
        return [x for x in names if x]


if __name__ == '__main__':
    scraper = FedreserveScraper()
    scraper.scrape()

