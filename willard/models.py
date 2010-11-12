import re
import urllib
import urllib2

try:
    import json
except ImportError:
    import simplejson as json

from django.db import models


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
    name = models.CharField(max_length=100)
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


class Client(models.Model):
    name = models.CharField(max_length=100)
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

    def __unicode__(self):
        return '%s (%s)' % (self.issue, self.code)

    @models.permalink
    def get_absolute_url(self):
        return ('willard_issue_detail', [self.code, ])


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
    signed_date = models.DateField(null=True)
    signer_email = models.EmailField()

    issues = models.ManyToManyField(IssueCode)
    foreign_entities = models.ManyToManyField(ForeignEntity)
    affiliated_orgs = models.ManyToManyField(AffiliatedOrg)
    lobbyists = models.ManyToManyField(Lobbyist)

    class Meta:
        unique_together = (('house_id', 'signed_date', ), )
        ordering = ('-signed_date', 'organization__name', )

    def __unicode__(self):
        return self.organization.name
