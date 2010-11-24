from cStringIO import StringIO
from decimal import Decimal
import re
import urllib
import urllib2
import zipfile

from django.core.management.base import BaseCommand
from django.db.models import *
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_unicode

from willard.models import *

import lxml.etree
from dateutil.parser import parse as dateparse


def get_form_body(year):
    url = 'http://disclosures.house.gov/ld/LDDownload.aspx'
    page = urllib2.urlopen(url).read()

    viewstate = re.search(r'id="__VIEWSTATE" value="(.*?)"', page).groups()[0]
    validation = re.search(r'id="__EVENTVALIDATION" value="(.*?)"', page).groups()[0]
    current_registration_val = re.search(r'(%s Registrations.*?)"' % year, page).groups()[0]

    return urllib.urlencode({'__VIEWSTATE': viewstate,
                             '__EVENTVALIDATION': validation,
                             'selFilesXML': current_registration_val, 
                             'btnDownloadXML': 'Download',
                             })


def get_xml(year, filename=None):
    if filename:
        zf = zipfile.ZipFile(open(filename, 'r'))

    else:
        body = get_form_body(year)
        url = 'http://disclosures.house.gov/ld/LDDownload.aspx'
        req = urllib2.Request(url, data=body)
        response = urllib2.urlopen(req)
        zf = zipfile.ZipFile(StringIO(response.read()))

    for f in zf.filelist:
        xml = zf.read(f.filename)
        yield f.filename.replace('.xml', ''), xml


def parse_xml(xml):
    root = lxml.etree.fromstring(xml)
    data = {'xml': xml, }

    # Convert xml into a dictionary
    for child in root.iterchildren():
        if list(child.iterchildren()):
            subchild_data = []
            for subchild in child.iterchildren():
                if list(subchild.iterchildren()):
                    # e.g. lobbyists
                    subsubchild_data = {}
                    for subsubchild in subchild.iterchildren():
                        subsubchild_data[subsubchild.tag] = subsubchild.text or ''
                    subchild_data.append(subsubchild_data)
                else:
                    subchild_data.append(subchild.text or '')
            data[child.tag] = subchild_data
            continue

        data[child.tag] = child.text or ''

    if data.get('effectiveDate'):
        data['effectiveDate'] = dateparse(data['effectiveDate']).strftime('%Y-%m-%d')
    else:
        data['effectiveDate'] = None
    if data.get('signedDate'):
        data['signedDate'] = dateparse(data['signedDate']).strftime('%Y-%m-%d')
    else:
        data['signedDate'] = None
    return data


def save_registration(data):
    if not data.get('organizationName'):
        return
    registrant, created = Organization.objects.get_or_create(
            slug = slugify(data['organizationName'])[:50],
                defaults = dict(
                    name=data.get('organizationName', ''),
                    address1=data.get('address1', ''),
                    address2=data.get('address2', ''),
                    city=data.get('city', ''),
                    state=data.get('state', '')[:2],
                    zip=data.get('zip', '')[:5],
                    country=data.get('country', ''),
                    prefix=data.get('prefix', ''),
                    principal_city=data.get('principal_city', ''),
                    principal_state=data.get('principal_state', '')[:2],
                    principal_zip=data.get('principal_zip', '')[:5],
                    principal_country=data.get('principal_country', ''),
                    general_description=data.get('registrantGeneralDescription', ''),
                    self_select=data.get('selfSelect', '')
                )
            )

    client, created = Client.objects.get_or_create(
            slug = slugify(data['clientName'])[:50],
                defaults = dict(
                    name=data.get('clientName', ''),
                    address=data.get('clientAddress', ''),
                    city=data.get('clientCity', ''),
                    state=data.get('clientState', '')[:2],
                    zip=data.get('clientZip', '')[:5],
                    principal_client_city=data.get('prinClientZip', '')[:5],
                    principal_client_state=data.get('prinClientState', '')[:2],
                    principal_client_zip=data.get('prinClientZip', '')[:5],
                    principal_client_country=data.get('prinClientCountry', ''),
                    general_description=data.get('clientGeneralDescription', '')[:255]
                )
            )

    # Find other registrations with this
    # house ID and check whether they are older
    # than this one. If they are, remove them.
    # If not, skip this one.
    if data.get('signedDate'):
        older = Registration.objects.filter(house_id=data['houseID'],
                                            signed_date__gt=data['signedDate'])
        newer = Registration.objects.filter(house_id=data['houseID'],
                                            signed_date__lte=data['signedDate'])
        if newer:
            return
        if older:
            older.delete()

    try:
        xml = data.get('xml', '').encode('unicode_escape', 'ignore')
    except UnicodeDecodeError:
        xml = ''

    registration, created = Registration.objects.get_or_create(
            house_id=data['houseID'],
            signed_date=data['signedDate'],
            defaults = dict(
                senate_id=data.get('senateID', ''),
                reg_type=data.get('regType', ''),
                organization=registrant,
                client=client,
                specific_issues=data.get('specific_issues', ''),
                report_year=data.get('reportYear', ''),
                report_type=data.get('reportType', ''),
                effective_date=data.get('effectiveDate', None),
                signer_email=data.get('signerEmail', ''),
                form_id=data.get('form_id', ''),
                xml=xml
                )
            )


    for lobbyist_data in data.get('lobbyists', []):
        try:
            if not lobbyist_data['lobbyistFirstName']:
                continue
        except TypeError:
            break
        lobbyist, created = Lobbyist.objects.get_or_create(
                first_name=lobbyist_data['lobbyistFirstName'],
                last_name=lobbyist_data['lobbyistLastName'],
                suffix=lobbyist_data['lobbyistSuffix'],
                defaults = dict(
                    covered_position=lobbyist_data['coveredPosition']
                )
            )
        registration.lobbyists.add(lobbyist)

    for affiliated in data.get('affiliatedOrgs', []):
        if not affiliated['affiliatedOrgName']:
            continue
        affiliated_org, created = AffiliatedOrg.objects.get_or_create(
                slug=slugify(affiliated['affiliatedOrgName'])[:50],
                defaults = dict(
                    name=affiliated['affiliatedOrgName'],
                    address=affiliated['affiliatedOrgAddress'],
                    city=affiliated['affiliatedOrgCity'],
                    state=affiliated['affiliatedOrgState'][:2],
                    zip=affiliated['affiliatedOrgZip'][:5],
                    country=affiliated['affiliatedOrgCountry'],
                    principal_org_city=affiliated['affiliatedOrgCity'],
                    principal_org_state=affiliated['affiliatedOrgState'][:2],
                    principal_org_country=affiliated['affiliatedOrgCountry'],
                )
            )
        registration.affiliated_orgs.add(affiliated_org)

    for entity in data.get('foreignEntities', []):
        if not entity['name']:
            continue

        contribution = entity.get('contribution', '').strip()
        if not contribution:
            contribution = Decimal('0')
        ownership_percentage = entity.get('ownership_Percentage', '').strip()
        if not ownership_percentage:
            ownership_percentage = Decimal('0')

        foreign_entity, created = ForeignEntity.objects.get_or_create(
                slug=slugify(entity['name'])[:50],
                defaults = dict(
                    name=entity['name'],
                    address=entity['address'],
                    city=entity['address'],
                    state=entity['state'][:2],
                    country=entity['country'],
                    principal_org_city=entity['prinCity'],
                    principal_org_state=entity['prinState'][:2],
                    principal_org_country=entity['prinCountry'],
                    contribution=contribution,
                    ownership_percentage=ownership_percentage
                )
            )
        registration.foreign_entities.add(foreign_entity)

    for issue in data.get('alis', []):
        if not issue.strip():
            continue
        try:
            issue_code = IssueCode.objects.get(code=issue)
        except IssueCode.DoesNotExist:
            issue_code = IssueCode.objects.create(code=issue, issue='')
        registration.issues.add(issue_code)

    print registration.house_id


def handle_amendments():
    """Amendments should be handled as the data is imported,
    but just in case any get through, we remove them here.
    """
    dupes = Registration.objects.order_by('house_id').values('house_id').annotate(c=Count('pk')).filter(c__gt=1)
    for d in dupes:
        for r in Registration.objects.filter(house_id=d['house_id']).order_by('-signed_date')[1:]:
            r.delete()


class Command(BaseCommand):

    def handle(self, *args, **options):
        if args:
            filename = args[0]
        else:
            filename = None
        for form_id, xml in get_xml(year=2010, filename=filename):
            print xml
            data = parse_xml(xml)
            data['form_id'] = form_id
            save_registration(data)
        handle_amendments()
