import re
import urllib2

from django.db import models
from django.db.models import signals
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.humanize.templatetags.humanize import ordinal

STATE_CHOICES = dict(STATE_CHOICES)

import MySQLdb

import name_tools
from doccloud_uploader import doccloud_upload

"""
class CommitteeManager(models.Manager):
    def get_query_set(self):
        #Committee.objects.exclude(expenditure__candidate__slug='')
        return super(CommitteeManager, self).get_query_set().exclude(expenditure__candidate__slug='')
"""

class IEOnlyCommittee(models.Model):
    """For committees that have submitted a letter saying
    they'll be accepting unlimited donations.
    """
    id = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=100)
    date_letter_submitted = models.DateField()
    pdf_url = models.URLField(verify_exists=False)
    doc_id = models.CharField(max_length=255) # For DocumentCloud id

    class Meta:
        ordering = ('-date_letter_submitted', )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('buckley_letter_detail', [self.id, ])

    def has_expenditures(self):
        committees = CommitteeId.objects.filter(fec_committee_id=self.id)
        if committees:
            return committees[0].committee
        return None

signals.post_save.connect(doccloud_upload, sender=IEOnlyCommittee, dispatch_uid='reporting.buckley')


class Committee(models.Model):
    #id = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    #objects = CommitteeManager()

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('buckley_committee_detail', [self.slug, ])

    def candidates(self, support_oppose):
        candidate_ids = self.expenditure_set.filter(support_oppose=support_oppose
                                                ).values_list('candidate', 
                                                              flat=True).distinct()
        return Candidate.objects.filter(id__in=candidate_ids)

    def candidates_supported(self):
        return self.candidates('S')

    def candidates_opposed(self):
        return self.candidates('O')

    def total(self, support_oppose=None):
        filter = {}
        if support_oppose:
            filter.update({'support_oppose': support_oppose})

        return self.expenditure_set.filter(**filter).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0

    def fec_id(self):
        return CommitteeId.objects.filter(committee=self)[0].fec_committee_id


class CommitteeId(models.Model):
    # Because some committees have more than one ID
    fec_committee_id = models.CharField(max_length=9)
    committee = models.ForeignKey(Committee)

    def __unicode__(self):
        return self.fec_committee_id


class Payee(models.Model):
    name = models.CharField(max_length=255)
    #street1 = models.CharField(max_length=255)
    #street2 = models.CharField(max_length=255)
    #city = models.CharField(max_length=255)
    #state = models.CharField(max_length=2)
    #zipcode = models.CharField(max_length=9)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('buckley_payee_detail', [self.slug, ])


class CandidateManager(models.Manager):
    def get_query_set(self):
        return super(CandidateManager, self).get_query_set().exclude(slug='no-candidate-listed')


class Candidate(models.Model):
    fec_id = models.CharField(max_length=9)
    fec_name = models.CharField(max_length=255)
    crp_id = models.CharField(max_length=9, blank=True)
    crp_name = models.CharField(max_length=255, blank=True)
    party = models.CharField(max_length=1, blank=True)
    office = models.CharField(max_length=1,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    state = models.CharField(max_length=2, blank=True)
    district = models.CharField(max_length=2)
    slug = models.SlugField()

    objects = CandidateManager()

    class Meta:
        ordering = ('fec_name', )

    def __unicode__(self):
        return self.crp_name or self.fec_name

    @models.permalink
    def get_absolute_url(self):
        return ('buckley_candidate_detail', [self.slug, ])

    def race(self):
        if self.office == 'S' or self.district.startswith('S'):
            return '%s-Senate' % self.state
        else:
            return '%s-%s' % (self.state, self.district.lstrip('0'))

    def full_race_name(self):
        if self.office == 'S' or self.district.startswith('S'):
            return '%s Senate' % STATE_CHOICES[self.state]
        else:
            return '%s %s' % (STATE_CHOICES[self.state], ordinal(self.district))

    def last_first(self):
        prefix, first, last, suffix = name_tools.split(self.__unicode__())
        return re.sub(r'\s+([^\w])', r'\1', '%s %s, %s' % (last, suffix, first))

    def seat(self):
        try:
            if self.fec_id:
                return {'H': 'House', 'S': 'Senate', 'P': 'president'}[self.fec_id[0]]
            else:
                return ''
        except KeyError:
            return None

    def committees(self, support_oppose):
        committee_ids = self.expenditure_set.filter(support_oppose=support_oppose).values_list('committee', flat=True).distinct()
        return Committee.objects.filter(id__in=committee_ids)

    def committees_supporting(self):
        return self.committees('S')

    def committees_opposing(self):
        return self.committees('O')

    def total(self, support_oppose=None):
        filter = {}
        if support_oppose:
            filter.update({'support_oppose': support_oppose})

        return self.expenditure_set.filter(**filter).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0

    def total_supporting(self):
        return self.total('S')

    def total_opposing(self):
        return self.total('O')

    def total_by_election_type(self, election_type, support_oppose=None):
        filter = {}
        exclude = {}
        if support_oppose:
            filter.update({'support_oppose': support_oppose})

        if election_type in ('P', 'G'):
            filter.update({'election_type': election_type})
        else:
            exclude.update({'election_type__in': ['P', 'G',]})

        return self.expenditure_set.filter(**filter).exclude(**exclude).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0



class Expenditure(models.Model):
    image_number = models.BigIntegerField()
    #form_type = models.CharField(max_length=10)
    committee = models.ForeignKey(Committee)
    payee = models.ForeignKey(Payee)
    #expenditure_form = models.CharField(max_length=3, blank=True)
    expenditure_purpose = models.CharField(max_length=255)
    expenditure_date = models.DateField(null=True)
    expenditure_amount = models.DecimalField(max_digits=19, decimal_places=2)
    support_oppose = models.CharField(max_length=1, 
                                      choices=(('S', 'Support'), ('O', 'Oppose'))
                                      )
    election_type = models.CharField(max_length=1,
                                      choices=(('P', 'Primary'), ('G', 'General'))
                                      )
    candidate = models.ForeignKey(Candidate)
    transaction_id = models.CharField(max_length=32)
    #memo_code = models.CharField(max_length=1, blank=True)
    #memo_text = models.CharField(max_length=255)
    receipt_date = models.DateField()
    filing_number = models.IntegerField()
    amendment = models.CharField(max_length=2)
    #election_type = models.CharField(max_length=5)
    #election_year = models.CharField(max_length=4)

    race = models.CharField(max_length=16) # denormalizing
    pdf_url = models.URLField(verify_exists=False)

    class Meta:
        ordering = ('-expenditure_date', )
        unique_together = (('image_number', 'transaction_id'), )

    def __unicode__(self):
        return str(self.image_number)

    @models.permalink
    def get_absolute_url(self):
        return ('buckley_expenditure_detail', [self.committee.slug, self.pk, ])

    def election_type_full(self):
        if self.election_type == 'G':
            return 'general election'
        elif self.election_type == 'P':
            return 'primary'
        return ''

    def election_type_for_detail_page(self):
        if self.election_type == 'G':
            return 'General'
        elif self.election_type == 'P':
            return 'Primary'
        else:
            return 'Other'

    def get_pdf_url(self):
        # First see if there are any other expenditures
        # with the same image number that already have
        # the PDF's URL stored.
        others = Expenditure.objects.filter(image_number=self.image_number).exclude(pdf_url='')
        if others:
            return others[0].pdf_url

        url = 'http://images.nictusa.com/cgi-bin/fecimg/?%s' % self.committee.fec_id()
        page = urllib2.urlopen(url).read()
        match = re.search(r'(\/pdf\/\d{3}\/%(imnum)s\/%(imnum)s\.pdf)' % {'imnum': self.image_number}, page)
        if match:
            pdf_path = match.group()
            return 'http://images.nictusa.com%s' % pdf_path
        return ''
