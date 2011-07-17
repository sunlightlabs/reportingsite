import re

from dateutil.parser import parse as dateparse
import lxml.html
import requests
import warnings

from pymongo import Connection
warnings.simplefilter("ignore")
import pyPdf

from scraper import Scraper


class SECScraper(Scraper):

    def __init__(self):
        self.base_url = 'http://sec.gov'
        self.agency = 'SEC'

    def get_homepage(self):
        url = 'http://sec.gov/spotlight/regreformcomments.shtml'
        return requests.get(url).content

    def get_comment_urls(self, page):
        return [self.base_url + x for x in re.findall(r'<a href="(.*?)">are available', page)]

    def scrape(self):
        page = self.get_homepage()
        comment_urls = self.get_comment_urls(page)

        for url in comment_urls:
            for data in self.parse_comment_page(url):
                self.save_data(data)

    def get_category(self, page):
        try:
            category = lxml.html.fromstring(page).cssselect('h1')[0].text_content().split('\n')[1].strip()
        except IndexError:
            try:
                category = lxml.html.fromstring(page).cssselect('h1')[0].text_content().split(':')[1].strip()
            except IndexError:
                category = re.search(r'Comments on (.*)$', lxml.html.fromstring(page).cssselect('h1')[0].text_content()).groups()[0]
        return category

    def parse_comment_page(self, url):
        page = requests.get(url).content
        category = self.get_category(page)
        meeting_section = re.search(r'<a name="meetings" id="meetings">.*', page, re.S)
        if not meeting_section:
            #print 'No meetings', url
            return

        doc = lxml.html.fromstring(meeting_section.group())
        rows = doc.cssselect('tr')
        for row in rows:
            cells = row.cssselect('td')
            try:
                date = dateparse(cells[0].text_content())
            except ValueError:
                continue

            meeting = cells[1].cssselect('a')[0]
            pdf_url = self.base_url +  meeting.attrib['href']
            meeting_title = meeting.text_content()
            meeting = self.parse_meeting_description(meeting_title)
            meeting.update({'url': pdf_url,
                            'pdf_url': pdf_url,
                            'meeting_time': date,
                            'category': category, })
            yield meeting


    def parse_meeting_description(self, text):
        regex = re.compile(r'''^Memorandum from (?:the )?(?P<from>.*?)(?:[Rr]egarding|re:) (?:an? )?(?P<meeting_time>(?:January|February|March|April|May|June|July|August|September|October|November|December) \d\d?, \d{4})?,? ?(?P<type>.+)(?:with )(?P<attendees>.*)''')
        m = regex.search(text)
        if not m:
            return {'meeting_time': None,
                    'from': None,
                    'visitors': None,
                    'type': None,
                    'description': text, }
        data = m.groupdict()
        data['description'] = text
        data['visitors'] = re.sub(r'(r|R)epresentatives? (of|from) ', '', data['attendees'])
        return data


if __name__ == '__main__':
    scraper = SECScraper()
    scraper.scrape()
