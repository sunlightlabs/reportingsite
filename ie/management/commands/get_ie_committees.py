"""Get a list of independent expenditure committees
and when they submitted their statement of organization.
"""
import csv
from collections import deque
import datetime
import re
import time
import urllib2

from django.template.defaultfilters import slugify
from django.core.management.base import NoArgsCommand

from ie.models import Committee


class Command(NoArgsCommand):

    help = "Update our database with newly registered independent expenditure committees."
    requires_model_validation = False

    def handle_noargs(self, **options):
        body = 'filerid=&name=&treas=&city=&img_num=&state=&party=&type=I&submit=Send+Query'
        url = 'http://images.nictusa.com/cgi-bin/fecimg/'
        request = urllib2.Request(url, body)
        response = urllib2.urlopen(request)
        page = response.read()
        for data in parse_committee_list(page):
            committee, created = Committee.objects.get_or_create(**data)
            print committee

            time.sleep(.5)


def get_committee_data(committee_id):
    url = 'http://query.nictusa.com/cgi-bin/fecimg/?%s' % committee_id
    page = urllib2.urlopen(url).read()

    name_m = re.search(r'<FONT SIZE=5><B>(.*?)<', page)
    if name_m:
        name = name_m.groups()[0]
    else:
        name = ''

    treasurer_m = re.search(r'Treasurer Name:<\/B><\/TD><TD>(.*?)<', page)
    if treasurer_m:
        treasurer = treasurer_m.groups()[0]
    else:
        treasurer = ''

    org_lines = re.findall(r'STATEMENT OF ORGANIZATION.*?<\/TR', page, re.S)
    dates = []
    for line in org_lines:
        date = re.search(r'(?P<month>\d\d)\/(?P<day>\d\d)\/(?P<year>\d\d\d\d)', line, re.S)
        if not date:
            continue
        date = deque(date.groups())
        date.rotate()
        date = [int(x) for x in date]
        dates.append(datetime.date(*date))

    if dates:
        create_date = sorted(dates)[0]
    else:
        create_date = None

    return dict(
            name=name,
            treasurer=treasurer,
            date_of_organization=create_date)


def parse_committee_list(page):
    rows = re.findall(r'<tr>.*?<\/tr>', page, re.I | re.S)
    if not rows:
        yield None

    for row in rows[1:]:
        row = row.replace('&nbsp;', '')
        (committee_id, 
                name, 
                city, 
                state, 
                party, 
                designation, 
                committee_type, 
                candidate_state, 
                candidate_office) = [x.strip() for x in re.findall(r'<td.*?>(.*?)<\/td>', row, re.I | re.S)]
        committee_id = re.search(r'C\d{8}', committee_id).group()

        if Committee.objects.filter(id=committee_id):
            continue

        committee_data = get_committee_data(committee_id) or {}
        if not committee_data:
            continue
        committee_data.update(
           {'id': committee_id,
            'city': city,
            'state': state,
            'party': party,
            'designation': designation,
            })
        yield committee_data


