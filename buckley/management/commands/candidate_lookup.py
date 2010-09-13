import csv
import sys
import time
import urllib2
import urllib

try:
    import json
except ImportError:
    import simplejson as json

def lookup_name(name):
    url = 'http://transparencydata.com/api/1.0/entities.json'
    body = urllib.urlencode({'apikey': '***REMOVED***', 'search': name})
    url += '?%s' % body
    print url
    data = urllib2.urlopen(url).read()
    data = [x for x in json.loads(data) if x['type'] == 'politician']
    print data

def _main():
    reader = csv.DictReader(sys.stdin)
    for name in set([row['S_O_CAND_NM'] for row in reader if row['S_O_CAND_NM']]):
        lookup_name(name)
        time.sleep(.25)
    """
    for row in reader:
        lookup_name(row['CMTE_NM'])
    """

if __name__ == '__main__':
    _main()
