import datetime
from cStringIO import StringIO
import re
import time
import urllib2

from django.core.management.base import NoArgsCommand

from buckley.models import IEOnlyCommittee

from dateutil.parser import parse as dateparse
import pyPdf


def get_already_submitted():
    """Create a list of committees that have submitted a letter
    that are already in our database.
    """
    return set(IEOnlyCommittee.objects.values_list('id', flat=True))

def get_committee_page(id):
    url = 'http://images.nictusa.com/cgi-bin/fecimg/?%s' % id
    response = urllib2.urlopen(url)
    return response.read()

def get_pdf_urls(page):
    rows = re.findall(r'(?:statement of organization|miscellaneous report to fec).*?<\/tr>', page, re.S | re.I)
    for row in rows:
        filed = re.search(r'\d\d\/\d\d\/\d\d\d\d', row)
        if filed:
            date = dateparse(filed.group()).date()
            if date > datetime.date.today() - datetime.timedelta(365):
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

            time.sleep(.15)
            page = get_committee_page(id)

            for url, date in get_pdf_urls(page):
                mentions_speechnow = parse_pdf(url)
                if mentions_speechnow:
                    IEOnlyCommittee.objects.create(
                            id=id,
                            name=get_committee_name(page),
                            date_letter_submitted=date,
                            pdf_url=url)
                    print id, url, get_committee_name(page), date
