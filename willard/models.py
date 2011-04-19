from collections import defaultdict
from operator import itemgetter
import datetime
import itertools
import urllib
import urllib2

from django.core.urlresolvers import reverse
from django.db import models, connection
from django.template.defaultfilters import slugify
from django.db.models import signals

from dateutil.relativedelta import relativedelta
from picklefield.fields import PickledObjectField
import lxml.etree
import MySQLdb


try:
    import json
except ImportError:
    import simplejson as json


def get_lobbyist_crp_name(raw_name):
    cursor = connection.cursor()
    cursor.execute("SELECT lobbyist_id, lobbyist FROM lobbyists where lobbyist_raw = %s LIMIT 1",
            [raw_name, ])
    if not cursor.rowcount:
        return '', ''
    return cursor.fetchone()


def get_ie_data(name):
    """Get data on an entity from Influence Explorer.
    """
    url = 'http://transparencydata.com/api/1.0/entities.json'
    body = urllib.urlencode({'apikey': '***REMOVED***',
                             'search': name, })
    url = '%s?%s' % (url, body)
    data = json.loads(urllib2.urlopen(url).read())
    return data


def create_counts_by_month(obj):
    counts = []
    cutoff = datetime.date.today() - relativedelta(months=12)
    cutoff = datetime.date(cutoff.year, cutoff.month, 1)
    curr = cutoff
    while curr <= datetime.date.today():
        counts.append(obj.registration_set.filter(received__month=curr.month,
                                                  received__year=curr.year).count())
        curr += relativedelta(months=1)
    return ','.join([str(x) for x in counts])


def combine_dupe_slugs(model):
    slugs = defaultdict(list)
    for obj in model.objects.all():
        slugs[slugify(obj.__unicode__())].append(obj)
    dupes = [(slug, objs) for slug, objs in slugs.items() if len(objs) > 1]
    for slug, objs in dupes:
        good = objs[0]
        bad = objs[1:]
        for obj in bad:
            obj.registration_set.update(**{model._meta.verbose_name: good, })
            obj.delete()


class Registrant(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    crp_name = models.CharField(max_length=255)

    # For sorting; crp_name if it exists, otherwise
    # name. This is also used to generate the slug.
    display_name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True)
    ie_data = PickledObjectField()

    class Meta:
        ordering = ('display_name', )

    def __unicode__(self):
        return self.display_name

    @models.permalink
    def get_absolute_url(self):
        return ('willard_registrant_detail', [self.slug, ])

    @models.permalink
    def get_rss_url(self):
        return ('willard_registrant_detail_feed', [self.slug, ])

    @models.permalink
    def get_csv_url(self):
        return ('willard_registrant_detail_api', [self.slug, 'csv', ])

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.crp_name = self.get_crp_name()
            self.display_name = self.crp_name or self.name
            self.ie_data = get_ie_data(self.display_name)
        super(Registrant, self).save(*args, **kwargs)

    def get_crp_name(self):
        cursor = connection.cursor()
        cursor.execute("SELECT registrant FROM lobbying WHERE registrant_raw = %s LIMIT 1",
                            [self.name, ])
        if not cursor.rowcount:
            return ''
        return cursor.fetchone()[0]

    def get_ie_data(self):
        return get_ie_data(self.display_name)

    def ie_id(self):
        if not len(self.ie_data):
            return None
        if len(self.ie_data) == 1:
            return self.ie_data[0]['id']
        m = [x for x in self.ie_data if x['name'] == self.display_name]
        if len(m):
            return m[0]['id']
        return None

    def ie_url(self):
        if not self.ie_id():
            return ''
        return 'http://influenceexplorer.com/organization/%s/%s' % (self.slug,
                                                                    self.ie_id())


class Client(models.Model):
    name = models.CharField(max_length=255)
    client_id = models.IntegerField()
    crp_name = models.CharField(max_length=255)

    # For sorting; crp_name if it exists, otherwise
    # name. This is also used to generate the slug.
    display_name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True)
    status = models.BooleanField()
    ie_data = PickledObjectField()

    class Meta:
        ordering = ('display_name', )

    def __unicode__(self):
        return self.display_name

    @models.permalink
    def get_absolute_url(self):
        return ('willard_client_detail', [self.slug, ])

    @models.permalink
    def get_rss_url(self):
        return ('willard_client_detail_feed', [self.slug, ])

    @models.permalink
    def get_csv_url(self):
        return ('willard_client_detail_api', [self.slug, 'csv', ])

    def save(self, *args, **kwargs):
        if self.id is None:
            self.crp_name = self.get_crp_name()
            self.display_name = self.crp_name or self.name
            self.ie_data = get_ie_data(self.display_name)
        super(Client, self).save(*args, **kwargs)

    def get_crp_name(self):
        cursor = connection.cursor()
        cursor.execute("SELECT client FROM lobbying WHERE client_raw = %s LIMIT 1",
                            [self.name.strip(), ])
        if not cursor.rowcount:
            return ''
        return cursor.fetchone()[0]

    def get_ie_data(self):
        return get_ie_data(self.display_name)

    def ie_id(self):
        if not len(self.ie_data):
            return None
        if len(self.ie_data) == 1:
            return self.ie_data[0]['id']
        m = [x for x in self.ie_data if x['name'] == self.display_name]
        if len(m):
            return m[0]['id']
        return None

    def ie_url(self):
        if not self.ie_id():
            return ''
        return 'http://influenceexplorer.com/organization/%s/%s' % (self.slug,
                                                                    self.ie_id())



class Issue(models.Model):
    issue = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    # Denormalizing counts by issue for the past 12 months.
    registration_count = models.IntegerField()

    # A comma-separated list of the number of registrations
    # for this issue over the past 12 months.
    counts_by_month = models.CharField(max_length=100)

    # Denormalizing counts by issue for the past 30 days.
    past_month_count = models.IntegerField()

    # A comma-separated list of the number of registrations
    # for this issue over the past 30 days.
    counts_by_day = models.CharField(max_length=200)

    class Meta:
        ordering = ('issue', )

    def __unicode__(self):
        return self.issue

    @models.permalink
    def get_absolute_url(self):
        return ('willard_issue_detail', [self.slug, ])

    def denormalize_by_month(self):
        month_counts = defaultdict(int)
        for date in self.registration_set.values_list('received', flat=True):
            month_counts['-'.join([str(date.year), str(date.month)])] += 1

        for year_month, count in month_counts.items():
            year, month = year_month.split('-')
            issue_by_month, created = IssueByMonth.objects.get_or_create(
                    issue=self,
                    month=month,
                    year=year,
                    defaults=dict(num=count)
                    )
            issue_by_month.num = count
            issue_by_month.save()

    def create_counts_by_month(self):
        by_month = self.issuebymonth_set.values('year', 'month', 'num')
        issue_counts = []
        cutoff = datetime.date.today() - relativedelta(months=12)
        cutoff = datetime.date(cutoff.year, cutoff.month, 1)
        curr = cutoff

        while curr <= datetime.date.today():
            issue_counts.append(sum([x['num'] for x in by_month if x['year'] == str(curr.year) and x['month'] == str(curr.month)]))
            curr += relativedelta(months=1)
        self.counts_by_month = ','.join([str(x) for x in issue_counts])
        self.save()

    def create_counts_by_day(self):
        last_date = Registration.objects.order_by('-received').values_list('received', flat=True)[0].date()
        month_cutoff = last_date - datetime.timedelta(30)

        registrations_by_day = dict()
        for date, group in itertools.groupby(self.registration_set.filter(received__gte=month_cutoff).values_list('received', flat=True), lambda x: x.date()):
            registrations_by_day[date] = len(list(group))

        # Fill in any missing dates with 0
        curr = month_cutoff
        while curr <= last_date:
            if curr not in registrations_by_day:
                registrations_by_day[curr] = 0
            curr += datetime.timedelta(1)

        registrations_by_day = sorted(registrations_by_day.items(), key=itemgetter(0))
        return ','.join([str(x[1]) for x in registrations_by_day])

    def past_month_num(self):
        last_date = Registration.objects.order_by('-received').values_list('received', flat=True)[0].date()
        month_cutoff = last_date - datetime.timedelta(30)
        return self.registration_set.filter(received__gte=month_cutoff).count()

    def denormalize_registration_count(self):
        cutoff = datetime.date.today() - relativedelta(months=12)
        cutoff = datetime.date(cutoff.year, cutoff.month, 1)
        self.registration_count = self.registration_set.filter(received__gte=cutoff).count()
        self.save()


class IssueByMonth(models.Model):
    """Denormalization of list of issues by month.
    """
    issue = models.ForeignKey(Issue, db_index=True)
    month = models.CharField(max_length=2, db_index=True)
    year = models.CharField(max_length=4, db_index=True)
    num = models.IntegerField()


class CoveredPosition(models.Model):
    position = models.TextField()

    def __unicode__(self):
        return self.position


class Lobbyist(models.Model):
    name = models.CharField(max_length=255)
    covered_positions = models.ManyToManyField(CoveredPosition)
    crp_name = models.CharField(max_length=255)
    crp_id = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    ie_data = PickledObjectField()

    denormalized_registrants = PickledObjectField()
    denormalized_covered_positions = PickledObjectField()
    registration_count = models.IntegerField()
    latest_registration = PickledObjectField()
    latest_client_name = models.CharField(max_length=255)
    latest_registration_date = models.DateField()

    class Meta:
        ordering = ('display_name', )

    def __unicode__(self):
        return self.display_name

    @models.permalink
    def get_absolute_url(self):
        return ('willard_lobbyist_detail', [self.slug, ])


    def save(self, *args, **kwargs):
        if not self.display_name:
            self.crp_id, self.crp_name = self.get_crp_name()
            self.display_name = self.crp_name or self.name
            #self.ie_data = get_ie_data(self.display_name)
        super(Lobbyist, self).save(*args, **kwargs)

    def get_crp_name(self):
        cursor = connection.cursor()
        cursor.execute("SELECT lobbyist_id, lobbyist FROM lobbyists where lobbyist_raw = %s LIMIT 1",
                [self.name.strip(), ])
        if not cursor.rowcount:
            return '', ''
        return cursor.fetchone()

    def get_ie_data(self):
        return get_ie_data(self.display_name)

    def ie_id(self):
        if not len(self.ie_data):
            return None
        return self.ie_data[0]['id']

    def ie_url(self):
        if not self.ie_id():
            return ''
        return 'http://influenceexplorer.com/individual/%s/%s' % (self.slug,
                                                                    self.ie_id())
    def registrants(self):
        registrants = Registrant.objects.none()
        for registration in self.registration_set.all():
            registrants = registrants | registration.registrant
        return registrants.distinct()

    def positions(self):
        """Check each covered position against
        each other position to try to determine
        whether they're actually different positions
        or just written differently.
        """
        from Levenshtein import distance
        positions = self.denormalized_covered_positions
        if not positions:
            return []

        distinct = [positions[0], ]
        for position1 in positions:
            min_distance = min([distance(position1, x) for x in distinct])
            if min_distance > 20:
                distinct.append(position1)
        if 'n/a' in distinct:
            del(distinct[distinct.index('n/a')])
        if 'None' in distinct:
            del(distinct[distinct.index('None')])
        return distinct



class AffiliatedOrganization(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    ppb_country = models.CharField(max_length=100)

    registration_count = models.IntegerField()
    latest_registration = PickledObjectField()


    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )

    @models.permalink
    def get_absolute_url(self):
        return ('willard_affiliated_detail', [self.slug, ])


class RegistrationManager(models.Manager):
    def get_query_set(self):
        return super(RegistrationManager, self).get_query_set().filter(amended=False)


class Registration(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    reg_type = models.CharField(max_length=24)
    registrant = models.ForeignKey(Registrant)
    client = models.ForeignKey(Client)
    received = models.DateTimeField()
    year = models.CharField(max_length=4)
    issues = models.ManyToManyField(Issue)
    specific_issue = models.TextField()

    xml = models.TextField()

    # Denormalize the list of issues
    denormalized_issues = PickledObjectField()

    lobbyists = models.ManyToManyField(Lobbyist)

    affiliated_organizations = models.ManyToManyField(AffiliatedOrganization)

    # This registration has been amended
    amended = models.BooleanField(default=False)

    objects = RegistrationManager()

    # All objects, even those that have been amended.
    all_objects = models.Manager()

    class Meta:
        ordering = ('-received', )

    def __unicode__(self):
        return self.registrant.name

    def save(self, *args, **kwargs):
        """If this is an amendment, mark the
        amended filing as such.
        """
        if self.reg_type == 'REGISTRATION AMENDMENT':
            amended = Registration.objects.filter(registrant=self.registrant,
                                                  client=self.client,
                                                  received__lt=self.received
                                              ).exclude(pk=self.pk)
            for registration in amended:
                registration.amended = True
                registration.save()
        super(Registration, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('willard_registration_detail', [self.registrant.slug,
                                                self.id, ])

    def pdf_url(self):
        return 'http://soprweb.senate.gov/index.cfm?event=getFilingDetails&filingID=%s' % self.id

    def as_dict(self):
        registration_dict = {'senate_id': self.id,
                             'registration_type': self.reg_type,
                             'registrant': {'name': self.registrant.display_name,
                                            'path': self.registrant.get_absolute_url(), },
                             'client': {'name': self.client.display_name,
                                        'path': self.client.get_absolute_url(), },
                             'received': str(self.received),
                             'issues': [],
                             'specific_issue': self.specific_issue, }
        for issue in self.denormalized_issues:
            registration_dict['issues'].append({'issue': issue.issue,
                                                'path': issue.get_absolute_url(), })
        return registration_dict

    def as_csv(self):
        return [self.id,
                self.reg_type,
                self.registrant.display_name,
                self.client.display_name,
                str(self.received),
                '|'.join([x.issue for x in self.denormalized_issues]),
                self.specific_issue.replace('\n', ' '), ]

    def save_lobbyists(self):
        """Because the lobbyist fields were added after
        some registrations had already been saved, we need
        to go back and add lobbyists for the registrations
        that already exist.
        """
        if self.lobbyists.count():
            return

        filing = lxml.etree.fromstring(self.xml)
        lobbyists = filing.find('Lobbyists')
        if lobbyists is None:
            return

        lobbyist = None

        for lobbyist_item in lobbyists.iterchildren():
            lobbyist_dict = lobbyist_item.attrib
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
                            latest_registration_date=self.received
                            )
                        )
                self.lobbyists.add(lobbyist)

            if not lobbyist:
                continue

            if covered_position:
                lobbyist.covered_positions.add(covered_position)

            if created:
                lobbyist.denormalized_registrants = set([self.registrant, ])
            else:
                lobbyist.denormalized_registrants = lobbyist.denormalized_registrants.union(set([self.registrant, ]))

            lobbyist.registration_count += 1

            latest_registration = lobbyist.registration_set.order_by('-received')[0]
            lobbyist.latest_registration = {'client': latest_registration.client,
                                            'received': latest_registration.received,
                                            'url': latest_registration.get_absolute_url(), }
            lobbyist.denormalized_covered_positions = [x.position for x in lobbyist.covered_positions.all()]

            lobbyist.save()


    def save_affiliated(self):
        if self.affiliated_organizations.count():
            return

        filing = lxml.etree.fromstring(self.xml)
        for org in filing.xpath('//Org'):
            name = org.attrib['AffiliatedOrgName']
            slug = slugify(name)[:50]
            country = org.attrib['AffiliatedOrgCountry']
            ppb_country = org.attrib['AffiliatedOrgPPBCcountry']

            affiliated, created = AffiliatedOrganization.objects.get_or_create(
                    slug=slug,
                    defaults=dict(
                        name=name,
                        slug=slug,
                        ppb_country=ppb_country,
                        country=country,
                        registration_count=0
                        )
                    )

            self.affiliated_organizations.add(affiliated)

            affiliated.registration_count += 1
            affiliated.latest_registration = self
            affiliated.save()


class PostEmploymentNotice(models.Model):
    body = models.CharField(max_length=10)
    first = models.CharField(max_length=100)
    middle = models.CharField(max_length=50)
    last = models.CharField(max_length=100)
    office_name = models.CharField(max_length=100)
    begin_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = (('body', 'first', 'last', 'office_name', ))

    def __unicode__(self):
        return '%s, %s %s' % (self.last.title(),
                              self.first.title(),
                              self.middle.title())
                                

    def get_absolute_url(self):
        return '%s#%s' % (reverse('willard_postemployment_list'),
                          self.pk)

    def days_left(self):
        diff = (self.end_date - datetime.date.today()).days
        if diff < 0:
            return ''
        return diff


class ForeignLobbying(models.Model):
    registration_number = models.IntegerField()
    registrant_name = models.CharField(max_length=255)
    registrant_status = models.CharField(max_length=255)
    registration_date = models.DateField()
    registrant_termination_date = models.DateField(null=True)
    alias = models.CharField(max_length=255)
    doing_business_as = models.CharField(max_length=255)

    document_type = models.CharField(max_length=255)
    stamped = models.DateField()

    short_form_name = models.CharField(max_length=255)
    short_form_registration_date = models.DateField(null=True)
    short_form_status = models.CharField(max_length=255)
    short_form_termination_date = models.DateField(null=True)

    supplemental_end_date = models.DateField(null=True)

    foreign_principal_country = models.CharField(max_length=255)
    foreign_principal_name = models.CharField(max_length=255)
    fp_registration_date = models.DateField(null=True)
    fp_termination_date = models.DateField(null=True)
    fp_status = models.CharField(max_length=255)

    pdf_url = models.URLField(verify_exists=False, unique=True)

    doc_id = models.CharField(max_length=255) # For DocumentCloud id

    def __unicode__(self):
        return '%s: %s (%s)' % (self.registrant_name,
                                self.document_type,
                                self.stamped.strftime('%Y-%m-%d'))

    @models.permalink
    def get_absolute_url(self):
        return ('willard_fara_filing', [self.id, ])

    def indefinite_article(self):
        if self.document_type[0].lower() in ['a', 'e', 'i', 'o', 'u', ]:
            return 'an'
        return 'a'


import base64
import json
import socket
import time
import urllib2
from cStringIO import StringIO

from buckley import MultipartPostHandler


USERNAME = '***REMOVED***'
PASSWORD = '***REMOVED***'

def doccloud_upload(sender, **kwargs):
    """Via http://www.muckrock.com/blog/using-the-documentcloud-api/
    """
    filing = kwargs['instance']
    if filing.doc_id:
        return

    filename = r'/tmp/fara.pdf'
    tf = open(filename, 'wb')
    tf.write(urllib2.urlopen(filing.pdf_url).read())
    tf.close()

    socket.setdefaulttimeout(25)

    params = {'title': '%s Foreign Agents Registration Act filing' % filing.registrant_name,
              'source': 'FARA Registration Unit',
              'file': open(filename, 'rb'), #StringIO(urllib2.urlopen(filing.pdf_url).read()),
              'access': 'public',
              }
    url = '/upload.json'
    opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
    request = urllib2.Request('https://www.documentcloud.org/api/%s' % url, params)
    auth = base64.encodestring('%s:%s' % (USERNAME, PASSWORD))[:-1]
    request.add_header('Authorization', 'Basic %s' % auth)

    try:
        ret = opener.open(request).read()
        info = json.loads(ret)
        filing.doc_id = info['id']
        filing.save()
    except urllib2.URLError, exc:
        print 'url error'
        print exc
        pass

    time.sleep(1)

signals.post_save.connect(doccloud_upload, sender=ForeignLobbying, dispatch_uid='reporting.willard')
