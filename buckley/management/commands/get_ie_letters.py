import datetime
from cStringIO import StringIO
import logging
import re
import socket
import time
import urllib2

from django.core.management.base import NoArgsCommand

from buckley.models import IEOnlyCommittee

from dateutil.parser import parse as dateparse
import pyPdf

# So our HTTP requests don't timeout as quickly
socket.setdefaulttimeout(60)

logging.basicConfig(filename='ie_letter_errors.log', level=logging.DEBUG)

def get_already_submitted():
    """Create a list of committees that have submitted a letter
    that are already in our database.
    """
    return set(IEOnlyCommittee.objects.values_list('id', flat=True))

def get_committee_page(id):
    url = 'http://images.nictusa.com/cgi-bin/fecimg/?%s' % id
    try:
        response = urllib2.urlopen(url)
    except urllib2.URLError:
        logging.debug('URLError on %s' % url)
        return None
    return response.read()

def get_pdf_urls(page):
    rows = re.findall(r'(?:statement of organization|miscellaneous report to fec).*?<\/tr>', page, re.S | re.I)
    for row in rows:
        filed = re.search(r'\d\d\/\d\d\/\d\d\d\d', row)
        if filed:
            date = dateparse(filed.group()).date()
            if date > datetime.date.today() - datetime.timedelta(15):
                match = re.search(r'\/pdf.*?\.pdf', row)
                if match:
                    yield 'http://images.nictusa.com%s' % match.group(), date

def parse_pdf(url):
    pdf = pyPdf.PdfFileReader(StringIO(urllib2.urlopen(url).read()))
    first_page = pdf.getPage(0).extractText()
    if re.search('speech\s?now', first_page, re.I | re.S):
        return True

    return False

def get_committee_name(page):
    match = re.search(r'<B>(.*?)<\/B>', page)
    if match:
        return match.groups()[0]
    return None

class Command(NoArgsCommand):
    help = """Get a list of independent expenditure committees that have submitted
    a letter saying they will raise unlimited contributions."""
    requires_model_validation = False

    def handle_noargs(self, **options):
        body = 'filerid=&name=&treas=&city=&img_num=&state=&party=&type=I&submit=Send+Query'
        url = 'http://images.nictusa.com/cgi-bin/fecimg/'
        request = urllib2.Request(url, body)
        response = urllib2.urlopen(request)
        page = response.read()

        already = get_already_submitted()
        committee_ids = set(re.findall(r'C\d{8}', page)).difference(already)

        for id in committee_ids:

            time.sleep(.25)
            page = get_committee_page(id)

            if not page:
                continue

            for url, date in get_pdf_urls(page):
                mentions_speechnow = parse_pdf(url)
                if mentions_speechnow:
                    IEOnlyCommittee.objects.create(
                            id=id,
                            name=get_committee_name(page),
                            date_letter_submitted=date,
                            pdf_url=url)
                    print id, url, get_committee_name(page), date
