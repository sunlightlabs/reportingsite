import re
import time
import urllib2

from django.core.management.base import BaseCommand, CommandError

import MySQLdb

cursor = MySQLdb.Connection('localhost', 'reporting', '***REMOVED***', 'reporting').cursor()

def get_candidates():
    cursor.execute("SELECT * from all_candidates")
    fieldnames = [x[0] for x in cursor.description]
    for row in cursor.fetchall():
        row = dict(zip(fieldnames, row))

        if not row['crp_id']:
            continue

        if row['incumbent'] == 1:
            row['type'] = 'C'
        else:
            row['type'] = 'I'

        yield row


def get_contributors(row):
    time.sleep(1)
    url = 'http://www.opensecrets.org/politicians/contrib.php?cycle=2010&cid=%(crp_id)s&type=%(type)s'
    fields = ['crp_id', 'state', 'district', 'candidate', 'rank', 'contributor', 'total', 'individuals', 'pacs', ]

    page = urllib2.urlopen(url % row).read()
    print url % row
    m = re.search(r'<table id="topContrib".*?<\/table>', page)
    if not m:
        yield {}

    table = m.group()
    trs = re.findall(r'<tr>.*?<\/tr>', table)
    for tr in trs[1:]:
        cells = [row['crp_id'], row['state'], row['district'], row['candidate'], ] + [re.sub(r'<.*?>', '', cell) for cell in re.findall(r'<td.*?<\/td>', tr)]
        data = dict(zip(fields, cells))
        data['individuals'] = data['individuals'].replace(',', '').replace('$', '')
        data['pacs'] = data['pacs'].replace(',', '').replace('$', '')
        data['total'] = data['total'].replace(',', '').replace('$', '')

        yield data



def clear_contributors(cid):
    cursor.execute("DELETE FROM candidate_contributions WHERE candidate_crp_id = %s", [cid, ])


def save_contributor(contributor):
    cursor.execute("""INSERT INTO candidate_contributions
                        (candidate_crp_id, rank, contributor, individuals,
                        pacs, total)
                        VALUES
                        (%(crp_id)s, %(rank)s, %(contributor)s, %(individuals)s,
                        %(pacs)s, %(total)s)""", contributor)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for candidate in get_candidates():
            print candidate
            clear_contributors(candidate['crp_id'])

            for contributor in get_contributors(candidate):
                if not contributor:
                    continue
                print contributor
                save_contributor(contributor)
        """
        contributors = list(get_contributors())
        if contributors:
            crp_id = contributors[0]['crp_id']
            clear_contributors(cid)
            for contributor in contributors:
                print contributor
                save_contributor(contributor)
        """
