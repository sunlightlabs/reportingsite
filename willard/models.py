from collections import defaultdict
from cStringIO import StringIO
from operator import itemgetter
import os
import re
import urllib
import urllib2

try:
    import json
except ImportError:
    import simplejson as json

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models

import pyPdf
import scribd


def get_ie_data(name):
    """Get data on an entity from Influence Explorer.
    """
    url = 'http://transparencydata.com/api/1.0/entities.json'
    body = urllib.urlencode({'apikey': '***REMOVED***',
                             'search': name, })
    url = '%s?%s' % (url, body)
    data = json.loads(urllib2.urlopen(url).read())
    return data


class Organization(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    prefix = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    country = models.CharField(max_length=100)
    principal_city = models.CharField(max_length=100)
    principal_state = models.CharField(max_length=2)
    principal_zip = models.CharField(max_length=5)
    principal_country = models.CharField(max_length=100)
    general_description = models.CharField(max_length=255)
    self_select = models.BooleanField()

    ie_id = models.CharField(max_length=32)
    ie_name = models.CharField(max_length=100)

    class Meta:
        #unique_together = (('name', 'address1', 'address2', 'city', 'state', 'zip', 'country', ), )
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('willard_organization_detail', [self.slug, ])

    def ie_url(self):
        if self.ie_id:
            return 'http://influenceexplorer.com/organization/%s/%s' % (self.slug, self.ie_id)
        suffixes = ['Inc', 'P.C.', 'LLC', 'PLLC', ]
        plain_name = re.sub(r'(%s)' % '|'.join(suffixes), '', self.name)
        plain_name = re.sub(r'(\.|\,)', '', plain_name).strip()
        return 'http://influenceexplorer.com/search?query=%s' % plain_name

    def issue_counts(self):
        issues = defaultdict(int)
        for registration in self.registration_set.all():
            for issue_code in registration.issues.all():
                issues[issue_code] += 1
        return sorted(issues.items(), key=itemgetter(1), reverse=True)


class Client(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    principal_client_city = models.CharField(max_length=100)
    principal_client_state = models.CharField(max_length=2)
    principal_client_zip = models.CharField(max_length=5)
    principal_client_country = models.CharField(max_length=100)
    general_description = models.CharField(max_length=255)

    ie_id = models.CharField(max_length=32)
    ie_name = models.CharField(max_length=100)

    class Meta:
        #unique_together = (('name', 'address', 'city', 'state', 'zip', ), )
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('willard_client_detail', [self.slug, ])

    def ie_url(self):
        if self.ie_id:
            return 'http://influenceexplorer.com/organization/%s/%s' % (self.slug, self.ie_id)
        suffixes = ['Inc', 'P.C.', 'LLC', 'PLLC', ]
        plain_name = re.sub(r'(%s)' % '|'.join(suffixes), '', self.name)
        plain_name = re.sub(r'(\.|\,)', '', plain_name).strip()
        return 'http://influenceexplorer.com/search?query=%s' % plain_name


class Lobbyist(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=100)
    covered_position = models.CharField(max_length=100)

    class Meta:
        unique_together = (('first_name', 'last_name', 'suffix', ), )

    def __unicode__(self):
        return '%s %s %s' % (self.first_name, self.last_name, self.suffix)


class IssueCode(models.Model):
    code = models.CharField(max_length=3, unique=True)
    issue = models.CharField(max_length=100)

    # Denormalizing counts by issue code for the past 12 months.
    registration_count = models.IntegerField()

    # A comma-separated list of the number of registrations
    # for this issue over the past 12 months.
    counts_by_month = models.CharField(max_length=100)

    def __unicode__(self):
        return '%s (%s)' % (self.issue, self.code)

    @models.permalink
    def get_absolute_url(self):
        return ('willard_issue_detail', [self.code, ])

    def denormalize_by_month(self):
        month_counts = defaultdict(int)
        for date in self.registration_set.exclude(signed_date=None).values_list('signed_date', flat=True):
            month_counts['-'.join([str(date.year), str(date.month)])] += 1

        for year_month, count in month_counts.items():
            year, month = year_month.split('-')
            issue_code_by_month, created = IssueCodeByMonth.objects.get_or_create(
                    issue_code=self,
                    month=month,
                    year=year,
                    defaults=dict(num=count)
                    )
            issue_code_by_month.num = count
            issue_code_by_month.save()

    def create_counts_by_month(self):
        by_month = self.issuecodebymonth_set.values('year', 'month', 'num')
        issue_counts = []
        cutoff = datetime.date.today() - relativedelta(months=12)
        cutoff = datetime.date(cutoff.year, cutoff.month, 1)

        while curr <= datetime.date.today():
            issue_counts.append(sum([x['num'] for x in by_month if x['year'] == str(curr.year) and x['month'] == str(curr.month)]))
            curr += relativedelta(months=1)
        counts_by_month = ','.join([str(x) for x in issue_counts])
        self.save()



class IssueCodeByMonth(models.Model):
    """Denormalization of list of issue codes by month.
    """
    issue_code = models.ForeignKey(IssueCode, db_index=True)
    month = models.CharField(max_length=2, db_index=True)
    year = models.CharField(max_length=4, db_index=True)
    num = models.IntegerField()


class AffiliatedOrg(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    country = models.CharField(max_length=100)
    principal_org_city = models.CharField(max_length=100)
    principal_org_state = models.CharField(max_length=2)
    principal_org_country = models.CharField(max_length=100)

    class Meta:
        #unique_together = (('name', 'address', 'city', 'state', 'zip', ), )
        pass

    def __unicode__(self):
        return self.name


class ForeignEntity(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=100)
    principal_org_city = models.CharField(max_length=100)
    principal_org_state = models.CharField(max_length=2)
    principal_org_country = models.CharField(max_length=100)
    contribution = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    ownership_percentage = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    class Meta:
        #unique_together = (('name', 'address', 'city', 'state', ), )
        pass

    def __unicode__(self):
        return self.name


class Registration(models.Model):
    reg_type = models.CharField(max_length=1)
    organization = models.ForeignKey(Organization)
    client = models.ForeignKey(Client)
    senate_id = models.CharField(max_length=64)
    house_id = models.CharField(max_length=64)
    specific_issues = models.TextField()
    report_year = models.CharField(max_length=4)
    report_type = models.CharField(max_length=2)
    effective_date = models.DateField(null=True)
    signed_date = models.DateField(null=True, db_index=True)
    signer_email = models.EmailField()

    issues = models.ManyToManyField(IssueCode)
    foreign_entities = models.ManyToManyField(ForeignEntity)
    affiliated_orgs = models.ManyToManyField(AffiliatedOrg)
    lobbyists = models.ManyToManyField(Lobbyist)

    form_id = models.CharField(max_length=9, unique=True)
    xml = models.TextField()

    scribd_id = models.IntegerField(blank=True, null=True)
    scribd_url = models.URLField(u'Scribd URL', verify_exists=False, blank=True)
    scribd_access_key = models.CharField(max_length=100)

    class Meta:
        unique_together = (('house_id', 'signed_date', ), )
        ordering = ('-signed_date', 'organization__name', )

    def __unicode__(self):
        return self.organization.name

    @models.permalink
    def get_absolute_url(self):
        return ('willard_registration_detail', [self.organization.slug,
                                                self.form_id, ])

    def house_pdf_url(self):
        return 'http://disclosures.house.gov/ld/pdfform.aspx?id=%s' % self.form_id

    def upload_to_scribd(self):
        scribd.config(settings.SCRIBD_KEY, settings.SCRIBD_SECRET)
        filename = '/tmp/%s.pdf' % self.form_id

        url = 'http://disclosures.house.gov/ld/pdfform.aspx?id=%s' % self.form_id
        pdf = pyPdf.PdfFileReader(StringIO(urllib2.urlopen(url).read()))
        pdf.decrypt('') # Encrypted with a blank password
        output = pyPdf.PdfFileWriter()
        for pagenum in range(pdf.getNumPages()):
            output.addPage(pdf.getPage(pagenum))

        outputStream = open(filename, 'wb')
        output.write(outputStream)
        outputStream.close()

        fh = open(filename, 'rb')
        doc = scribd.api_user.upload(fh, access='private')
        fh.close()
        os.remove(filename)

        site = Site.objects.get_current()

        params = {'title': 'Registration by %s to lobby for %s (%s)' % (self.organization.name,
                                                                        self.client.name,
                                                                        self.form_id),
                  'description': 'This registration was filed with the House on %s' % self.signed_date.strftime('%B %d, %Y'),
                  'link_back_url': 'http://%s%s' % (site.domain, self.get_absolute_url()),
                  'category': 'Government Docs',
                  'access': 'public',
                  }
        scribd.update([doc, ], **params)

        collections = scribd.api_user.get_collections()
        collection = [x for x in collections if x.collection_name == 'Lobbyist Registrations']
        if collection:
            collection = collection[0]
            try:
                doc.add_to_collection(collection)
            except:
                pass

        self.scribd_id = doc.id
        self.scribd_url = doc.get_scribd_url()
        self.scribd_access_key = doc.get_attributes()['access_key']
        self.save()

        return doc
