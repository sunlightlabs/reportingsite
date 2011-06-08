from operator import itemgetter
import pprint
import re
import urllib
import urllib2

from django.core.management.base import BaseCommand, CommandError

from aors.models import AORDocument

import requests



class Command(BaseCommand):

    def handle(self, *args, **options):
        self.get_page()
        data = self.parse_page()
        self.save_data(data)


    def save_data(self, data):
        for aor_number, values in data.iteritems():
            for url, description in values['docs']:
                aor_doc, created = AORDocument.objects.get_or_create(
                                        doc_url=url,
                                        defaults=dict(
                                            aor_description=values['description'],
                                            aor_id=values['id'],
                                            aor_number=aor_number,
                                            org=values['org'],
                                            doc_description=description
                                            )
                                        )

    def parse_page(self):
        aors = re.findall(r'<a href="javascript:ao\(&quot;(\d+)&quot;\)"><strong>(.*?)<\/a><\/strong> <a href="javascript:ao\(&quot;\d+&quot;\)"><strong>(.*?)<\/a><\/strong>.*?<br>(.*?)<ul>', self.page, re.S)
        linkdata = re.findall(r'<A HREF\="javascript:ao1\((\d+), &quot;(\d+)\.pdf&quot;\)">(.*?)<\/A>', self.page)
        docurl = 'http://saos.nictusa.com/aodocs/%s.pdf'

        data = {}

        for aor in aors:
            id, ao, org, description = [x.strip() for x in aor]
            data[ao] = {'id': id, 
                        'org': org, 
                        'description': description, 
                        'docs': sorted([(docurl % x[1], x[2]) for x in linkdata if x[0] == id], key=itemgetter(1)),
                    }
            data[ao]
        return data


    def get_page(self):
        url = 'http://saos.nictusa.com/saos/searchao?SUBMIT=pending'
        params = {'KEYWORDS': '',
                  'AONUM': '',
                  'REQNAME': '',
                  'RESULTNUM': '-1',
                  'CURRSTATE': 'fec.saos.gui.BasicSearch',
                  'childsession': '0', }
        r = requests.post(url, 
                          data=params, 
                          headers={'Cookie': self.get_jsessionid(),
                                  }
                          )
        self.page = r.content


    def get_jsessionid(self):
        url = 'http://saos.nictusa.com/saos/searchao'
        r = requests.get(url)
        return r.headers['set-cookie']
