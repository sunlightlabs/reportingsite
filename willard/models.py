from collections import defaultdict
import datetime

from django.db import models

from dateutil.relativedelta import relativedelta
from picklefield.fields import PickledObjectField


class Registrant(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    crp_name = models.CharField(max_length=255)
    slug = models.SlugField()
    country = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    ie_id = models.CharField(max_length=32)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('willard_registrant_detail', [self.slug, ])


class Client(models.Model):
    name = models.CharField(max_length=255)
    client_id = models.IntegerField()
    crp_name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    is_state_or_local_gov = models.BooleanField()
    status = models.BooleanField()
    contact_name = models.CharField(max_length=255)

    ie_id = models.CharField(max_length=32)

    class Meta:
        ordering = ('name', )
        unique_together = (('name', 'state', ), )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('willard_client_detail', [self.slug, ])


class Issue(models.Model):
    issue = models.CharField(max_length=100)
    slug = models.SlugField()

    # Denormalizing counts by issue for the past 12 months.
    registration_count = models.IntegerField()

    # A comma-separated list of the number of registrations
    # for this issue over the past 12 months.
    counts_by_month = models.CharField(max_length=100)

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

    def denormalize_registration_count(self):
        self.registration_count = self.registration_set.count()
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
