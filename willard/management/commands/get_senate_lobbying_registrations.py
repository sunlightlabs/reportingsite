from cStringIO import StringIO
from optparse import make_option
import re
import urllib2
import zipfile

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from willard.models import *

import lxml.etree
from dateutil.parser import parse as dateparse


def get_zipfile_urls(year):
    url = 'http://www.senate.gov/legislative/Public_Disclosure/database_download.htm'
    page = urllib2.urlopen(url).read()
    zipfiles = re.findall(r'(%s_\d\.zip)' % year, page)
    base_url = 'http://soprweb.senate.gov/downloads/%s'
    return [base_url % filename for filename in zipfiles]


def get_xml(year, filename=None, all_quarters=False):
    if filename:
        zf = zipfile.ZipFile(open(filename, 'r'))
        for f in zf.filelist:
            xml = zf.read(f.filename)
            yield f.filename, xml

    else:
        urls = get_zipfile_urls(year)
        if not all_quarters:
            urls.reverse()
            urls = urls[:1]
        for url in urls:
            zipdata = urllib2.urlopen(url).read()
            zf = zipfile.ZipFile(StringIO(zipdata))
            for f in zf.filelist:
                xml = zf.read(f.filename)
                yield f.filename, xml


def parse_xml(xml):
    # Because the XML file may have errors that would
    # prevent it from being parsed by lxml, we split up
    # the filings into separate objects. This way if there
    # is a parsing error, it should fail on only a single 
    # filing entity, not the entire file.
    filings = re.findall(r'<filing.*?<\/filing>', xml, re.I | re.S)

    for filing_xml in filings:
        try:
            filing = lxml.etree.fromstring(filing_xml)
        except lxml.etree.XMLSyntaxError:
            continue

        data = {'xml': filing_xml, } # Store the raw XML

        # Only keep going if this is a registration
        # or an amendment to a registration
        if not dict(filing.items())['Type'].startswith('REGISTRATION'):
            continue

        data.update(dict(filing.items()))

        registrant = filing.find('Registrant')
        data['registrant'] = dict(registrant.items())
        client = filing.find('Client')
        data['client'] = dict(client.items())
        issues = filing.find('Issues') or []
        data['issues'] = [dict(issue.items())['Code'] for issue in issues]
        if len(issues):
            data['specific_issue'] = dict(issues[0].items()).get('SpecificIssue', '')
        else:
            data['specific_issue'] = ''

        yield data


def save_filing(data):
    if Registration.objects.filter(id=data['ID']):
        return

    slug = slugify(data['registrant']['RegistrantName'])[:50]
    try:
        registrant = Registrant.objects.get(slug=slug)
    except Registrant.DoesNotExist:
        try:
            registrant = Registrant.objects.get(id=data['registrant']['RegistrantID'])
        except Registrant.DoesNotExist:
            registrant = Registrant.objects.create(
                    slug=slug,
                    id=data['registrant']['RegistrantID'],
                    name=data['registrant']['RegistrantName'],
                    crp_name='')
            registrant.crp_name = registrant.get_crp_name()
            registrant.display_name = registrant.crp_name or registrant.name
            registrant.save()

    client, created = Client.objects.get_or_create(
            slug=slugify(data['client']['ClientName'])[:50],
            defaults=dict(
                name=data['client']['ClientName'],
                client_id=data['client']['ClientID'],
                crp_name='',
                status=int(data['client']['ClientStatus']))
            )
    if created:
        client.crp_name=client.get_crp_name()
        client.display_name = client.crp_name or client.name
        client.save()


    registration, created = Registration.objects.get_or_create(
            id=data['ID'],
            defaults=dict(
                reg_type=data['Type'],
                registrant=registrant,
                client=client,
                received=dateparse(data['Received']),
                year=data['Year'],
                specific_issue=data['specific_issue'],
                xml=data['xml'])
            )
    for registration_issue in data['issues']:
        issue, created = Issue.objects.get_or_create(
                slug=slugify(registration_issue)[:50],
                defaults=dict(
                    issue=registration_issue.title(),
                    registration_count=0,
                    counts_by_month='')
                )
        registration.issues.add(issue)
    
    # Denormalize list of issues
    registration.denormalized_issues = list(registration.issues.all())
    registration.save()


def denormalize():
    """Denormalize issue counts.
    """
    for issue in Issue.objects.all():
        issue.denormalize_by_month()
        issue.create_counts_by_month()
        issue.denormalize_registration_count()


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('--all_quarters',
                        action='store_true',
                        dest='all_quarters',
                        default=False,
                        help="Import all data for the given years"),
            make_option('--years',
                        action='store',
                        dest='years',
                        default='2010',
                        help="Years for which to import data. If multiple years are entered, all data for those years will be imported."),
            make_option('--filename',
                        action='store',
                        dest='filename',
                        default=None,
                        help="Override default behavior of downloading data from Senate website and use given file."),
            )

    def handle(self, *args, **options):
        filename = options['filename']
        all_quarters = options['all_quarters']
        years = options['years'].split(',')

        for year in years:

            for filename, xml in get_xml(year, filename, all_quarters):
                print filename
                for filing in parse_xml(xml):
                    save_filing(filing)
                    """
                    try:
                        save_filing(filing)
                    except Exception, e:
                        print Exception
                        print e
                        print filing
                        print
                    """

        # Find any clients or registrants without a display_name
        # and create one.
        for model in [Client, Registrant, ]:
            for obj in model.objects.filter(display_name=''):
                obj.crp_name = obj.get_crp_name()
                obj.display_name = obj.crp_name or obj.name
                obj.save()

        denormalize()
