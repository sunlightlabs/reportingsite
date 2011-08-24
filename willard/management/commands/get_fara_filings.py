from cStringIO import StringIO
import datetime
import re
import sys
import time
import urllib
import urllib2

import lxml.html
import pyPdf
from dateutil.parser import parse as dateparse

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from willard.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        url = 'https://efile.fara.gov/pls/apex/f?p=125:10:::NO::P10_DOCTYPE:ALL'

        page = urllib2.urlopen(url).read()
        doc = lxml.html.fromstring(page)
        form = doc.cssselect('form')[0]

        data = []
        for input in form.cssselect('input'):
            if input.attrib.get('name'):
                if input.attrib['name'] in ('p_t01', 'p_t02', 'p_t06', 'p_t07', 'p_request'):
                    continue
                data.append((input.attrib['name'], input.attrib['value']))

        start_date = datetime.date.today() - datetime.timedelta(14)
        end_date = datetime.date.today()

        data += [('p_t01', 'ALL'),
                 ('p_t02', 'ALL'),
                 ('p_t06', start_date.strftime('%m/%d/%Y')),
                 ('p_t07', end_date.strftime('%m/%d/%Y')),
                 ('p_request', 'SEARCH'),
                 ]

        #url = 'http://209.11.109.152/pls/htmldb/wwv_flow.accept'
        url = 'https://efile.fara.gov/pls/apex/wwv_flow.accept'

        req = urllib2.Request(url, data=urllib.urlencode(data))
        page = urllib2.urlopen(req).read()

        doc = lxml.html.fromstring(page)
        for filing in self.parse(doc):
            self.save_filing(filing)

    def save_filing(self, filing):
        print filing
        try:
            obj = ForeignLobbying.objects.create(**filing)
        except IntegrityError:
            print 'IntegrityError'
            return
        print obj

    def get_metadata(self, filing):
        url = filing['pdf_url']
        try:
            pdf = urllib2.urlopen(url).read()
        except urllib2.HTTPError:
            return None

        # We can save the PDF here and then upload it to Document Cloud.

        pdf = pyPdf.PdfFileReader(StringIO(pdf))
        text = pdf.getPage(0).extractText()
        print
        print text
        print
        metadata = {}
        for line in text.split('\n'):
            if line.find('=') > -1:
                k, v = line.split('=')
                k = k.title()
                if v == 'N/A':
                    v = ''
                metadata.update({k: v, })
        return metadata

    def parse(self, doc):
        rows = doc.cssselect('table.t14Standard tr')
        for row in rows[1:]:
            print lxml.html.tostring(row, pretty_print=True)
            filing = {}
            cells = row.cssselect('td')
            filing['pdf_url'] = cells[0].cssselect('a')[0].attrib.get('href')
            if ForeignLobbying.objects.filter(pdf_url=filing['pdf_url']):
                print 'Already exists: %s' % filing['pdf_url']
                continue

            fields = ['registration_number',
                      'registrant_name',
                      'document_type',
                      'stamped', ]
            filing.update(dict(zip(fields, [x.text_content() for x in cells[1:]])))
            filing['stamped'] = dateparse(filing['stamped'])
            '''
            try:
                metadata = self.get_metadata(filing)
            except:
                continue
            if metadata is None:
                print 'No metadata found: %s' % filing['pdf_url']
                continue

            filing.update(metadata)

            print filing
            try:
                filing = self.adjust_fieldnames(filing)
            except:
                continue

            for k, v in filing.iteritems():
                if k in ['registration_date', 'stamped', 'short_form_termination_date',
                         'short_form_registration_date', 'supplemental_end_date',
                         'fp_registration_date', 'fp_termination_date', 
                         'registrant_termination_date', ]:
                    if v:
                        filing[k] = dateparse(v).date()
                    else:
                        filing[k] = None

            '''
            time.sleep(1)
            yield filing

    mapping = {'Alias': 'alias',
                   'Document Type': 'document_type',
                   'Doing Business As': 'doing_business_as',
                   'Foreign Principal Country': 'foreign_principal_country',
                   'Foreign Principal Name': 'foreign_principal_name',
                   'Fp Registration Date': 'fp_registration_date',
                   'Fp Status': 'fp_status',
                   'Fp Termination Date': 'fp_termination_date',
                   'Registrant Status': 'registrant_status',
                   'Registrant Termination Date': 'registrant_termination_date',
                   'Registration Date': 'registration_date',
                   'Short Form Name': 'short_form_name',
                   'Short Form Registration Date': 'short_form_registration_date',
                   'Short Form Status': 'short_form_status',
                   'Short Form Termination Date': 'short_form_termination_date',
                   'Supplemental End Date': 'supplemental_end_date',
                   'document_type': 'document_type',
                   'pdf_url': 'pdf_url',
                   'registrant_name': 'registrant_name',
                   'registration_number': 'registration_number',
                   'stamped': 'stamped',
                   }
    def adjust_fieldnames(self, filing):
        new_filing = {}
        for k, v in self.mapping.iteritems():
            new_filing[v] = filing[k]

        return new_filing
