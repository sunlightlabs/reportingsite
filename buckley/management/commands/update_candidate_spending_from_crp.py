import csv
import re
import socket
import time
import urllib2

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from buckley.models import *


socket.setdefaulttimeout(1000)

STATES = ['AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC',
          'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN',
          'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO',
          'MP', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
          'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC',
          'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI',
          'WV', 'WY']


def clean_candidate_name(candidate):
    return re.sub(r' \(.*?\) ?\*?$', '', candidate)


def get_state_races(state):
    url = 'http://www.opensecrets.org/races/election.php?state=%s' % state
    page = urllib2.urlopen(url).read()

    table = re.search(r"<table class='datadisplay'>.*?<\/table>", page, re.S)
    if not table:
        return []

    table = table.group()
    rows = re.findall(r'<tr>.*?<\/tr>', table, re.S)

    data = []

    race = None

    for row in rows:
        race_re = re.search(r"<a href='(?P<race_url>.*?)'>(?P<race>.*?)<\/a>", row)
        if race_re:
            race = race_re.groupdict()['race']
            race_url = 'http://www.opensecrets.org%s' % race_re.groupdict()['race_url']

            race_page = urllib2.urlopen(race_url).read()
            candidates = {}
            for race_candidate, spent in re.findall(r'<h2>(?:<a.*?>)?(?P<candidate>.*?)(?:<\/a>)?<\/h2>.*?Spent:.*?(?P<spent>\$[,\d]+)', race_page):
                candidates[clean_candidate_name(race_candidate.strip())] = re.sub(r'[\$,]', '', spent)

        if not race:
            continue

        candidate_re = re.search(r"<td style='background-color:#\w{6};'>(?P<candidate>.*?)<td", row)
        if not candidate_re:
            continue

        candidate = candidate_re.groupdict()['candidate']

        m = re.search(r'\((?P<party>.*?)\)(?P<incumbent>\*?)$', candidate)
        incumbent = 'Y' if m.groupdict()['incumbent'] else 'N'
        party = m.groupdict()['party']

        candidate = clean_candidate_name(candidate)
        if candidate in candidates:
            spent = candidates[candidate]
        else:
            spent = 0

        raised_re = re.search(r'\$[\d,]+', row)
        raised = re.sub(r'[\$,]', '', raised_re.group())

        data.append({'state': state,
                     'race': race,
                     'candidate': candidate,
                     'party': party,
                     'incumbent': incumbent,
                     'spent': spent,
                     #'raised': raised
                     }
                     )

    return data


def update_spending(data):
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM all_candidates WHERE candidate = %(candidate)s AND state = %(state)s", data)
    if not cursor.rowcount:
        return None
    data['id'] = cursor.fetchone()[0]
    cursor.execute("UPDATE all_candidates SET spending = %(spent)s, timestamp = NOW() WHERE id = %(id)s", data)
    return id


class Command(BaseCommand):

    def handle(self, *args, **options):
        for state in states:
            print state
            time.sleep(1)
            for row in get_state_races(state):
                update_spending(row)
