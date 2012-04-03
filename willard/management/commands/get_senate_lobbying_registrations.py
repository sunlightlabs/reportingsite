from cStringIO import StringIO
from optparse import make_option
import re
import urllib2
import zipfile

from django.core.management.base import BaseCommand
from django.db import connection
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


def smart_unicode(s):
    # Could also try the below
    # but latin1 seems not to work
    # 'ascii', 'latin1', 'windows-1252',
    for enc in [ 'utf-8', 'utf-16']:
        try:
            s.decode(enc)
            return (enc)
        except UnicodeDecodeError:
            pass

    raise UnicodeDecodeError
        
def parse_xml(xml):
    # Because the XML file may have errors that would
    # prevent it from being parsed by lxml, we split up
    # the filings into separate objects. This way if there
    # is a parsing error, it should fail on only a single 
    # filing entity, not the entire file.
    #print "running parse_xml on %s" % xml
    
    encoding = smart_unicode(xml)
    print "Found encoding %s" % (encoding)
    filings = re.findall(r'<filing.*?<\/filing>', unicode(xml, encoding), re.I | re.S | re.U)
    print "Running regex!"
    for filing_xml in filings:
        print "running parse_xml on %s with encoding %s" % (filing_xml, encoding)
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

        lobbyists = filing.find('Lobbyists')
        if lobbyists:
            data['lobbyists'] = [x.attrib for x in lobbyists.iterchildren()]
        else:
            data['lobbyists'] = []

        yield data


def save_filing(data):
    print "Saving filing %s" % (data['registrant']['RegistrantName'])
    if Registration.all_objects.filter(id=data['ID']):
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
                    name=data['registrant']['RegistrantName'])

    client, created = Client.objects.get_or_create(
            slug=slugify(data['client']['ClientName'])[:50],
            defaults=dict(
                name=data['client']['ClientName'],
                client_id=data['client']['ClientID'],
                status=int(data['client']['ClientStatus']))
            )

    registration, created = Registration.all_objects.get_or_create(
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

    lobbyist = None

    for lobbyist_dict in data['lobbyists']:
        covered_position = None
        if lobbyist_dict.get('OfficialPosition'):
            covered_position, created = CoveredPosition.objects.get_or_create(
                    position=lobbyist_dict.get('OfficialPosition', '')
                    )
        # Check whether the lobbyist name line is blank
        # or refers to the lobbyist name listed above it.
        # If so, use the previous lobbyist name.
        name = lobbyist_dict['LobbyistName']
        if name.find('*') > -1: # used for notes
            continue
        if name and name not in (' ',
                                 "(CONT'D), (CONT'D)",
                                 '(CONTINUED), (CONTINUED)',
                                 '(CONTINUED), (CONTINUED',
                                 '-, -',
                                 '-----, -----',
                                 'ABOVE), (SEE',
                                 "'', ''",
                                 '", "',
                                 ):

            crp_id, crp_name = get_lobbyist_crp_name(lobbyist_dict['LobbyistName'])

            lobbyist, created = Lobbyist.objects.get_or_create(
                    slug=slugify(crp_name or lobbyist_dict['LobbyistName'])[:50],
                    defaults=dict(
                        display_name=crp_name or lobbyist_dict['LobbyistName'],
                        crp_name=crp_name,
                        crp_id=crp_id,
                        name=lobbyist_dict['LobbyistName'],
                        registration_count=0,
                        latest_registration_date=dateparse(data['Received']),
                        )
                    )
            registration.lobbyists.add(lobbyist)

        if not lobbyist:
            continue

        if covered_position:
            lobbyist.covered_positions.add(covered_position)

        if created:
            lobbyist.denormalized_registrants = set([registrant, ])
        else:
            lobbyist.denormalized_registrants = lobbyist.denormalized_registrants.union(set([registrant, ]))

        lobbyist.registration_count += 1

        latest_registration = lobbyist.registration_set.order_by('-received')[0]
        lobbyist.latest_registration = {'client': latest_registration.client,
                                        'received': latest_registration.received,
                                        'url': latest_registration.get_absolute_url(), }
        lobbyist.denormalized_covered_positions = [x.position for x in lobbyist.covered_positions.all()]

        lobbyist.save()

    
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


def get_lobbyist_crp_name(raw_name):
    cursor = connection.cursor()
    cursor.execute("SELECT lobbyist_id, lobbyist FROM lobbyists where lobbyist_raw = %s LIMIT 1",
            [raw_name, ])
    if not cursor.rowcount:
        return '', ''
    return cursor.fetchone()


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
                        default='2011',
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
        
        print "running command %s %s %s" % (filename, all_quarters, years)

        for year in years:

            for filename, xml in get_xml(year, filename, all_quarters):
                print " ** " + filename
                for filing in parse_xml(xml):
                    save_filing(filing)

        denormalize()
