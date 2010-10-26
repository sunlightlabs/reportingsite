from collections import defaultdict
from decimal import Decimal
import re
import socket
import urllib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

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
    description = models.TextField()

    tax_status = models.CharField(max_length=10,
            choices=(('501(c)(4)', '501(c)(4)'),
                     ('501(c)(5)', '501(c)(5)'),
                     ('501(c)(6)', '501(c)(6)'),
                     ('527', '527'),
                     ('FECA PAC', 'FECA PAC'),
                     ('FECA Party', 'FECA Party'),
                     ('Person', 'Person'),
            ),
            blank=True)

    has_donors = models.BooleanField()

    #transparencydata_id = models.CharField(max_length=40)

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

    def ie_total(self):
        return self.expenditure_set.filter(electioneering_communication=False).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0

    def ec_total(self):
        return self.expenditure_set.filter(electioneering_communication=True).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0

    def money_spent_on_candidate(self, candidate, support_oppose=None):
        filter = {'candidate': candidate}
        if support_oppose:
            filter['support_oppose'] = support_oppose
        amount = self.expenditure_set.filter(**filter).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0
        if not support_oppose:
            # Include electioneering communications
            amount += candidate.electioneering_expenditures.filter(committee=self).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0
        return amount

    def fec_id(self):
        return CommitteeId.objects.filter(committee=self)[0].fec_committee_id

    def ieonly_url(self):
        ieonly = IEOnlyCommittee.objects.filter(id=self.fec_id())
        if ieonly:
            return ieonly[0].get_absolute_url()
        return ''

    def all_candidates_with_amounts(self):
        ie_candidates = self.expenditure_set.order_by('candidate').values_list('candidate', flat=True).distinct().exclude(candidate=None)

        electioneering_candidates = []
        for expenditure in self.expenditure_set.filter(electioneering_communication=True):
            electioneering_candidates += list(expenditure.electioneering_candidates.order_by('id').values_list('id', flat=True))

        candidate_ids = set(list(ie_candidates) + electioneering_candidates)
        candidates = []
        for id in candidate_ids:
            candidate = Candidate.objects.get(id=id)
            if candidate in self.candidates_supported():
                support_oppose = 'Support'
            elif candidate in self.candidates_opposed():
                support_oppose = 'Oppose'
            else:
                support_oppose = '*'
            amount = self.money_spent_on_candidate(candidate)
            candidates.append({'candidate': candidate,
                                'support_oppose': support_oppose,
                                'amount': amount, })

        return candidates

    def combined_all_candidates_with_amounts(self):
        """Combine same electioneering comm. mentioning
        multiple candidates onto one line.
        """
        # key is candidates mentioned, value is 
        # queryset of expenditures
        expenditures = defaultdict(list)

        for expenditure in self.expenditure_set.all():
            if expenditure.electioneering_communication:
                expenditures[tuple(expenditure.electioneering_candidates.all())].append(expenditure)
            else:
                expenditures[tuple(Candidate.objects.filter(pk=expenditure.candidate.pk))].append(expenditure)


        # key is candidates mentioned, value is
        # dict of race (or 'multiple'), amount
        rows = {}
        for candidates, exps in expenditures.iteritems():
            amount = sum([x.expenditure_amount for x in exps])
            support_oppose = set()
            for exp in exps:
                if exp.electioneering_communication:
                    support_oppose = ['*',]
                    break
                if exp.support_oppose == 'S':
                    support_oppose.add('Support')
                elif exp.support_oppose == 'O':
                    support_oppose.add('Oppose')
                else:
                    support_oppose = ''
                    break

            if support_oppose != '':
                if len(support_oppose) > 1:
                    support_oppose = ''
                else:
                    support_oppose = list(support_oppose)[0]

            if len(candidates) == 1:
                rows[candidates] = {'race': candidates[0].race(),
                                    'amount': amount,
                                    'support_oppose': support_oppose,
                                    }
            else:
                if candidates:
                    if len(list(set([x.race() for x in candidates]))) > 1:
                        race = 'Multiple'
                    else:
                        race = candidates[0].race()
                else: # Some ECs have no candidate
                    race = ''

                slugs = ','.join([x.slug for x in candidates])

                rows[candidates] = {'race': race,
                                    'amount': amount, 
                                    'support_oppose': '*',
                                    'slugs': slugs,
                                    }

        return rows.items()

    def get_transparencydata_id(self):

        class RedirectHandler(urllib2.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers):   
                result = urllib2.HTTPRedirectHandler.http_error_302(
                                self, req, fp, code, msg, headers)              
                result.status = code                                
                return result

        body = urllib.urlencode({'query': self.name, })
        request = urllib2.Request('http://influenceexplorer.com/search?%s' % body)
        opener = urllib2.build_opener(RedirectHandler)
        f = opener.open(request)

        try:
            if f.status == 302:
                return f.url.split('/')[-1]
        except:
            pass

        return ''

    def get_address(self):
        url = 'http://query.nictusa.com/cgi-bin/fecimg/?%s' % self.fec_id()
        page = urllib2.urlopen(url).read()
        m = re.search(r'</B></FONT><BR><BR>(.*?)<TABLE', page, re.S)
        if not m:
            return ''

        return [x.replace('<BR>', '') for x in m.groups()[0].split('\n') if x]



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

    # Denormalizations
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    transparencydata_id = models.CharField(max_length=40, default='')

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

    def all_committees_with_amounts(self):
        ie_committees = self.expenditure_set.order_by('committee').values_list('committee', flat=True).distinct()
        electioneering_committees = self.electioneering_expenditures.order_by('committee').values_list('committee', flat=True).distinct()
        committee_ids = set(list(ie_committees) + list(electioneering_committees))
        committees = []
        for id in committee_ids:
            committee = Committee.objects.get(id=id)
            if committee in self.committees_supporting():
                support_oppose = 'Support'
            elif committee in self.committees_opposing():
                support_oppose = 'Oppose'
            else:
                support_oppose = '*'
            amount = committee.money_spent_on_candidate(self)
            committees.append({'committee': committee,
                               'support_oppose': support_oppose,
                               'amount': amount, })
        return committees

    def sole_all_committees_with_amounts(self):
        """Create a list of all committees that have expended for/against
        this candidate, with amounts, but only include expenditures/ECs
        that have referred to ONLY this candidate, as opposed to ones
        that have referred to another candidate as well.
        """
        # Include all IE committees that have
        # expended for/against this candidate;
        # IEs list only one candidate.
        ie_committee_ids = self.expenditure_set.order_by('committee').values_list('committee', flat=True).distinct()
        ie_committees = Committee.objects.filter(pk__in=ie_committee_ids)

        electioneering_expenditures_include = set()
        for ec in self.electioneering_expenditures.all():
            if ec.electioneering_candidates.count() == 1:
                electioneering_expenditures_include.add(ec.pk)

        electioneering_expenditures = Expenditure.objects.filter(pk__in=electioneering_expenditures_include)
        ec_committees = defaultdict(list)
        committees = {}
        for ec in electioneering_expenditures:
            ec_committees[ec.committee.pk].append(ec)

        for k, v in ec_committees.iteritems():
            committees[k] = {'committee': v[0].committee,
                             'support_oppose': '*',
                             'amount': sum([x.expenditure_amount for x in v]), }

        for committee in ie_committees:
            if committee in self.committees_supporting():
                support_oppose = 'Support'
            elif committee in self.committees_opposing():
                support_oppose = 'Oppose'
            else:
                support_oppose = '*'

            if committee.pk in committees:
                if committees[committee.pk]['support_oppose'] == '*':
                    support_oppose = '*'

            amount = committee.money_spent_on_candidate(self)
            committees[committee.pk] = {'committee': committee,
                                        'support_oppose': support_oppose,
                                        'amount': amount, }

        return committees.values()


    def joint_electioneering(self):
        """Create a list of electioneering communications
        that have mentioned this candidate and at least
        one other candidate.
        """
        include = []
        for ec in self.electioneering_expenditures.all():
            if ec.electioneering_candidates.count() > 1:
                include.append(ec)

        return include


    def committees_supporting(self):
        return self.committees('S')

    def committees_opposing(self):
        return self.committees('O')

    def total(self, support_oppose=None):
        filter = {}
        if support_oppose:
            filter.update({'support_oppose': support_oppose})

        return self.expenditure_set.filter(**filter).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0

    def total_including_electioneering(self):
        ie = self.expenditure_set.aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0
        electioneering = self.electioneering_expenditures.aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0
        return ie + electioneering

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

    def electioneering_total(self):
        return self.electioneering_expenditures.aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0

    def sole_electioneering_total(self, election_type=None):
        """Total of electioneering communications
        that mention ONLY this candidate (as opposed
        to ones that mention other candidates as well).
        """
        include = []
        filter = {}
        exclude = {}
        if election_type:
            if election_type in ('P', 'G'):
                filter.update({'election_type': election_type, })
            else:
                exclude.update({'election_type__in': ['P', 'G', ]})

        for ec in self.electioneering_expenditures.filter(**filter).exclude(**exclude):
            if ec.electioneering_candidates.count() == 1:
                include.append(ec.pk)

        if not include:
            return 0

        return Expenditure.objects.filter(pk__in=include).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0

    def sole_total(self):
        ies = self.expenditure_set.aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0
        electioneering = self.sole_electioneering_total()
        return ies + electioneering

    def electioneering_total_by_election_type(self, election_type=None):
        filter = {'electioneering_communication': True, }
        exclude = {}
        if election_type:
            if election_type in ('P', 'G'):
                filter.update({'election_type': election_type})
            else:
                exclude.update({'election_type__in': ['P', 'G', ]})

        return self.electioneering_expenditures.filter(**filter).exclude(**exclude).aggregate(amount=models.Sum('expenditure_amount'))['amount'] or 0

    def denormalize(self):
        self.total_expenditures = (self.total() + self.sole_electioneering_total()) or 0
        self.expenditures_supporting = self.total_supporting() or 0
        self.expenditures_opposing = self.total_opposing() or 0
        self.save()

    def get_transparencydata_id(self):
        if not self.crp_id:
            return ''

        body = urllib.urlencode({'apikey': '***REMOVED***',
                                 'namespace': 'urn:crp:recipient', 
                                 'id': self.crp_id, })
        url = 'http://transparencydata.com/api/1.0/entities/id_lookup.json?%s' % body
        response = urllib2.urlopen(url).read()
        data = json.loads(response)
        if data:
            return data[0]['id']

        return ''

    def influence_explorer_url(self):
        if not self.transparencydata_id:
            return None
        return 'http://influenceexplorer.com/politician/%s/%s' % (self.slug,
                                                                  self.transparencydata_id)


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
    candidate = models.ForeignKey(Candidate, blank=True, null=True) # NULL for electioneering
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

    electioneering_communication = models.BooleanField(default=False)

    # Electioneering communications reports sometimes 
    # multiple candidates for the same communication.
    # For those we need to use a ManyToManyField
    electioneering_candidates = models.ManyToManyField(Candidate, related_name='electioneering_expenditures')

    timestamp = models.DateTimeField()


    class Meta:
        ordering = ('-expenditure_date', )
        unique_together = (('image_number', 'transaction_id'), )

    def __unicode__(self):
        return str(self.image_number)

    @models.permalink
    def get_absolute_url(self):
        if self.candidate:
            return ('buckley_candidate_committee_detail', [self.candidate.slug, self.committee.slug, ])
        slugs = ','.join([x.slug for x in self.electioneering_candidates.all()])
        if slugs:
            return ('buckley_candidate_committee_detail', [slugs, self.committee.slug, ])
        return ('buckley_committee_detail', [self.committee.slug, ])

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
        body = 'filerid=%s&name=&treas=&city=&img_num=%s&state=&party=&type=&submit=Send+Query' % (self.committee.fec_id(), self.image_number)
        base_url = 'http://images.nictusa.com'
        search_url = '%s/cgi-bin/fecimg/' % base_url
        req = urllib2.Request(search_url, body)
        page = urllib2.urlopen(req).read()
        match = re.search("src='(\/pdf.*?)#", page)
        if match:
            return '%s%s' % (base_url, match.groups()[0])
        return ''

    def candidate_slugs(self):
        """For electioneering communications, return a comma-concatenated list
        of candidates' slugs.
        """
        if not self.electioneering_candidates.all():
            return ''

        return ','.join([x.slug for x in self.electioneering_candidates.all()])


class Contribution(models.Model):
    committee = models.ForeignKey(Committee)
    filing_number = models.IntegerField()
    transaction_id = models.CharField(max_length=32)
    name = models.CharField(max_length=255)
    contributor_type = models.CharField(max_length=10)
    date = models.DateField()
    employer = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    street1 = models.CharField(max_length=100)
    street2 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=9)
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    aggregate = models.DecimalField(max_digits=19, decimal_places=2)
    memo = models.CharField(max_length=100)
    url = models.URLField(verify_exists=False)
    data_row = models.TextField()
    data_row_hash = models.CharField(max_length=32, db_index=True) # This would normally have a unique key, but some data rows are blank.

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('committee', 'filing_number', 'transaction_id', 'name', 'date', 'employer', 'occupation',
                            'street1', 'street2', 'city', 'state', 'zipcode', 'amount', 'aggregate', 
                            'memo', ), )


"""Caching data for the totals page.
"""
class Total(models.Model):
    ie_total = models.DecimalField(max_digits=19, decimal_places=2)
    ec_total = models.DecimalField(max_digits=19, decimal_places=2)
    total = models.DecimalField(max_digits=19, decimal_places=2)
    republican_support_nonparty = models.DecimalField(max_digits=19, decimal_places=2)
    republican_support_party = models.DecimalField(max_digits=19, decimal_places=2)
    republican_support_total = models.DecimalField(max_digits=19, decimal_places=2)
    republican_oppose_nonparty = models.DecimalField(max_digits=19, decimal_places=2)
    republican_oppose_party = models.DecimalField(max_digits=19, decimal_places=2)
    republican_oppose_total = models.DecimalField(max_digits=19, decimal_places=2)
    democrat_support_nonparty = models.DecimalField(max_digits=19, decimal_places=2)
    democrat_support_party = models.DecimalField(max_digits=19, decimal_places=2)
    democrat_support_total = models.DecimalField(max_digits=19, decimal_places=2)
    democrat_oppose_nonparty = models.DecimalField(max_digits=19, decimal_places=2)
    democrat_oppose_party = models.DecimalField(max_digits=19, decimal_places=2)
    democrat_oppose_total = models.DecimalField(max_digits=19, decimal_places=2)

class TopCommittee(models.Model):
    committee = models.ForeignKey(Committee)
    amount = models.DecimalField(max_digits=19, decimal_places=2)

class TopPartyCommittee(models.Model):
    committee = models.ForeignKey(Committee)
    amount = models.DecimalField(max_digits=19, decimal_places=2) 

class TopRace(models.Model):
    race = models.CharField(max_length=16)
    amount = models.DecimalField(max_digits=19, decimal_places=2)

class TopCandidate(models.Model):
    candidate = models.ForeignKey(Candidate)
    amount = models.DecimalField(max_digits=19, decimal_places=2)
