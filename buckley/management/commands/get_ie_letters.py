from optparse import make_option
import datetime
from cStringIO import StringIO
import logging
import re
import socket
import time
import urllib2

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from buckley.models import IEOnlyCommittee

from dateutil.parser import parse as dateparse
import pyPdf

# So our HTTP requests don't timeout as quickly
socket.setdefaulttimeout(60)

logging.basicConfig(filename='ie_letter_errors.log', level=logging.DEBUG)

def smart_title(s):
    s = s.title()
    to_uppercase = ['Pac', ]
    regex = re.compile(r'(%s)' % '|'.join([r'\b%s\b' % x for x in to_uppercase]))
    return regex.sub(lambda x: x.group().upper(), s)

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

    try:
        return response.read()
    except socket.timeout:
        logging.debug('socket timeout on %s' % url)
        return None

def get_pdf_urls(page):
    rows = re.findall(r'(?:statement of organization|miscellaneous report to fec).*?<\/tr>', page, re.S | re.I)
    for row in rows:
        filed = re.search(r'\d\d\/\d\d\/\d\d\d\d', row)
        if filed:
            date = dateparse(filed.group()).date()
            if date > datetime.date.today() - datetime.timedelta(1000):
                match = re.search(r'\/pdf.*?\.pdf', row)
                if match:
                    yield 'http://images.nictusa.com%s' % match.group(), date

def parse_pdf(url):
    pdf = pyPdf.PdfFileReader(StringIO(urllib2.urlopen(url).read()))
    for pagenum in range(pdf.numPages):
        page = pdf.getPage(pagenum).extractText()
        if re.search('spe?ecc?h\s?now', page, re.I | re.S):
            return True

        if re.search(r'Carey v\.? FEC', page, re.I | re.S):
            return True

        if re.search(r'independent expenditure(-| )only', page, re.I | re.S):
            return True

        if re.search(r'intends to make independent expenditures', page, re.I | re.S):
            return True

    return False

def get_committee_name(page):
    match = re.search(r'<B>(.*?)<\/B>', page)
    if match:
        return smart_title(match.groups()[0])
    return None


def save_checked_url(url):
    with open(r'/projects/reporting/log/fec_pdfs_checked.log', 'a') as fh:
        fh.write(url + '\n')


class Command(BaseCommand):
    help = """Get a list of independent expenditure committees that have submitted
    a letter saying they will raise unlimited contributions."""
    requires_model_validation = False

    option_list = BaseCommand.option_list + (
            make_option('--cids',
                action='store',
                dest='cids',
                default=None,
                help='Comma-separated list of committees to check for IE-only letters.'),
    ) 

    def handle(self, *args, **options):
        body = 'filerid=&name=&treas=&city=&img_num=&state=&party=&type=I&submit=Send+Query'
        url = 'http://images.nictusa.com/cgi-bin/fecimg/'
        request = urllib2.Request(url, body)
        response = urllib2.urlopen(request)
        page = response.read()

        checked = [x.strip() for x in open(r'/projects/reporting/log/fec_pdfs_checked.log', 'r')]

        if options.get('cids'):
            committee_ids = options.get('cids').split(',')
        else:
            already = get_already_submitted()
            committee_ids = set(re.findall(r'C\d{8}', page)).difference(already)

        for id in committee_ids:

            time.sleep(.25)
            page = get_committee_page(id)

            if not page:
                continue

            for url, date in get_pdf_urls(page):
                if url in checked and not options.get('cids'):
                    continue
                mentions_speechnow = parse_pdf(url)
                if mentions_speechnow:
                    try:
                        IEOnlyCommittee.objects.create(
                                id=id,
                                name=get_committee_name(page),
                                date_letter_submitted=date,
                                pdf_url=url)
                    except IntegrityError:
                        continue

                    print id, url, get_committee_name(page), date

                save_checked_url(url)
