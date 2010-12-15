from collections import defaultdict
from operator import itemgetter
import datetime
import itertools
import urllib
import urllib2

from django.db import models
from django.template.defaultfilters import slugify

from dateutil.relativedelta import relativedelta
from picklefield.fields import PickledObjectField
import MySQLdb

try:
    import json
except ImportError:
    import simplejson as json


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

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.crp_name = self.get_crp_name()
            self.display_name = self.crp_name or self.name
            self.ie_data = get_ie_data(self.display_name)
        super(Registrant, self).save(*args, **kwargs)

    def get_crp_name(self):
        cursor = MySQLdb.Connection('localhost', 'campfin', 'campfin', 'campfin').cursor()
        cursor.execute("SELECT registrant FROM lobbying WHERE registrant_raw = %s LIMIT 1",
                            self.name)
        if not cursor.rowcount:
            return ''
        return cursor.fetchone()[0]

    def get_ie_data(self):
        return get_ie_data(self.display_name)

    def ie_id(self):
        if len(self.ie_data):
            return self.ie_data[0]['id']
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

    def save(self, *args, **kwargs):
        if self.id is None:
            self.crp_name = self.get_crp_name()
            self.display_name = self.crp_name or self.name
            self.ie_data = get_ie_data(self.display_name)
        super(Client, self).save(*args, **kwargs)

    def get_crp_name(self):
        cursor = MySQLdb.Connection('localhost', 'campfin', 'campfin', 'campfin').cursor()
        cursor.execute("SELECT client FROM lobbying WHERE client_raw = %s LIMIT 1",
                            self.name.strip())
        if not cursor.rowcount:
            return ''
        return cursor.fetchone()[0]

    def get_ie_data(self):
        return get_ie_data(self.display_name)

    def ie_id(self):
        if not len(self.ie_data):
            return None
        return self.ie_data[0]['id']

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

    class Meta:
        ordering = ('-received', )

    def __unicode__(self):
        return self.registrant.name

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
                self.specific_issue, ]
