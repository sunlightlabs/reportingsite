from django.db import models

"""Simplified version of buckley that's truer to the FEC data"""

CYCLE_DATES = {'2010': ('2009-01-01', '2010-12-31', ),
               '2012': ('2011-01-01', '2012-12-31', ),
               }

class Candidate(models.Model):
    cycle = models.CharField(max_length=4)
    fec_id = models.CharField(max_length=9, blank=True)
    fec_name = models.CharField(max_length=255)
    crp_id = models.CharField(max_length=9, blank=True, null=True)
    crp_name = models.CharField(max_length=255, blank=True, null=True)
    td_name = models.CharField(max_length=255, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True) 
    party = models.CharField(max_length=3, blank=True)
    office = models.CharField(max_length=1,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    seat_status = models.CharField(max_length=1,
                                  choices=(('I', 'Incumbent'), ('C', 'Challenger'), ('O', 'Open'))
                                  )
    candidate_status = models.CharField(max_length=1,
                                        choices=(('C', 'STATUTORY CANDIDATE'), ('F', 'STATUTORY CANDIDATE FOR FUTURE ELECTION'), ('N', 'NOT YET A STATUTORY CANDIDATE'), ('P', 'STATUTORY CANDIDATE IN PRIOR CYCLE'))
                                         )
    # state is from the candidate's address (?)                                     
    state_address = models.CharField(max_length=2, blank=True)
    district = models.CharField(max_length=2, blank=True)
    slug = models.SlugField()
    campaign_com_fec_id = models.CharField(max_length=9, blank=True)
    # Denormalizations
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    transparencydata_id = models.CharField(max_length=40, default='', null=True)

    class Meta:
        ordering = ('fec_name', )

    def __unicode__(self):
        return self.crp_name or self.fec_name


    @models.permalink
    def get_absolute_url(self):
        return ('buckley_cycle_candidate_detail', [self.cycle, self.slug, ])

    def race(self):
        if self.office == 'P':
            return 'President'
        elif self.office == 'S' or self.district.startswith('S'):
            return '%s-Senate' % self.state
        else:
            return '%s-%s' % (self.state, self.district.lstrip('0'))

    def full_race_name(self):
        if self.office == 'P':
            return 'President'
        elif self.office == 'S' or self.district.startswith('S'):
            try:
                return '%s Senate' % STATE_CHOICES[self.state]
            except KeyError:
                return 'Senate'
        else:
            try:
                return '%s %s' % (STATE_CHOICES[self.state], ordinal(self.district))
            except KeyError:
                return ''

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
class Committee(models.Model):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, null=True)
    fec_id = models.CharField(max_length=9, blank=True)
    slug = models.SlugField(max_length=100)
    party = models.CharField(max_length=3, blank=True)
    # Josue Larose has 62 pacs and counting... 
    treasurer = models.CharField(max_length=38, blank=True, null=True)
    street_1 = models.CharField(max_length=34, blank=True, null=True)
    street_2 = models.CharField(max_length=34, blank=True, null=True)
    city =models.CharField(max_length=18, blank=True, null=True)
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    
    designation = models.CharField(max_length=1,
                                   blank=False,
                                   null=True,
                                   choices=[('A', 'Authorized by Candidate'),
                                            ('J', 'Joint Fund Raiser'),
                                            ('P', 'Principal Committee of Candidate'),
                                            ('U', 'Unauthorized'),
                                            ('B', 'Lobbyist/Registrant PAC'),
                                            ('D', 'Leadership PAC')])

    ctype = models.CharField(max_length=1,
                             blank=False,
                             null=True,
                             choices=[('C', 'Communication Cost'),
                                      ('D', 'Delegate'),
                                      ('H', 'House'),
                                      ('I', 'Independent Expenditure (Not a Committee'),
                                      ('N', 'Non-Party, Non-Qualified'),
                                      ('P', 'Presidential'),
                                      ('Q', 'Qualified, Non-Party'),
                                      ('S', 'Senate'),
                                      ('X', 'Non-Qualified Party'),
                                      ('Y', 'Qualified Party'),
                                      ('Z', 'National Party Organization'),
                                      ('E', 'Electioneering Communication')])

    tax_status = models.CharField(max_length=10,
            choices=(('501(c)(4)', '501(c)(4)'),
                     ('501(c)(5)', '501(c)(5)'),
                     ('501(c)(6)', '501(c)(6)'),
                     ('527', '527'),
                     ('FECA PAC', 'FECA PAC'),
                     ('FECA Party', 'FECA Party'),
                     ('Person', 'Person'),
            ),
            blank=True, null=True)
    filing_frequency = models.CharField(max_length=1, 
            choices=[('A', 'ADMINISTRATIVELY TERMINATED'),
                     ('D', 'DEBT'),
                     ('M', 'MONTHLY FILER'),
                     ('Q', 'QUARTERLY FILER'),
                     ('T', 'TERMINATED'),
                     ('W', 'WAIVED')
                     ])
    interest_group_cat= models.CharField(max_length=1,choices=[
                            ('C', 'CORPORATION'),
                            ('L', 'LABOR ORGANIZATION'),
                            ('M', 'MEMBERSHIP ORGANIZATION'),
                            ('T', 'TRADE ASSOCIATION'),
                            ('V', 'COOPERATIVE'),
                            ('W', 'CORPORATION WITHOUT CAPITAL STOCK')
                          ])
    connected_org_name=models.CharField(max_length=65, blank=True)
    candidate_id = models.CharField(max_length=9,blank=True)
    candidate_office = models.CharField(max_length=1, blank=True)
    
    has_donors = models.NullBooleanField()
    has_expenditures = models.NullBooleanField()
    is_superpac = models.NullBooleanField()
    
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)


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
        ordering = ('name', )

    def __unicode__(self):
        return self.name


class Expenditure(models.Model):
    cycle = models.CharField(max_length=4, null=True)
    image_number = models.BigIntegerField()
    line_hash = models.BigIntegerField(null=True)
    raw_committee_id = models.CharField(max_length=9, null=True)
    committee = models.ForeignKey(Committee, null=True)
    payee = models.CharField(max_length=255)
    expenditure_purpose = models.CharField(max_length=255)
    expenditure_date = models.DateField(null=True)
    expenditure_amount = models.DecimalField(max_digits=19, decimal_places=2)
    support_oppose = models.CharField(max_length=1, 
                                      choices=(('S', 'Support'), ('O', 'Oppose'))
                                      )
    election_type = models.CharField(max_length=1,
                                      choices=(('P', 'Primary'), ('G', 'General'), ('S', 'Special'))
                                      )
    candidate_name=models.CharField(max_length=90, null=True, blank=True)                                  
    raw_candidate_id=models.CharField(max_length=9, null=True)
    candidate = models.ForeignKey(Candidate, blank=True, null=True) # NULL for electioneering
    candidate_party_affiliation=models.CharField(max_length=10,null=True)
    office = models.CharField(max_length=1,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              , null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    district = models.CharField(max_length=2, blank=True, null=True)
    transaction_id = models.CharField(max_length=32)
    receipt_date = models.DateField()
    filing_number = models.IntegerField()
    amendment = models.CharField(max_length=2)

    race = models.CharField(max_length=16) # denormalizing
    pdf_url = models.URLField(verify_exists=False)

    electioneering_communication = models.BooleanField(default=False)

    # Electioneering communications reports sometimes 
    # multiple candidates for the same communication.
    # For those we need to use a ManyToManyField
    electioneering_candidates = models.ManyToManyField(Candidate, related_name='electioneering_expenditures')
    
    # Should we disregard this line item because it appears later in an amended filing?
    superceded_by_amendment=models.BooleanField(default=False)
    amends_earlier_filing = models.BooleanField(default=False)
    # if this entry is amended by a more recent entry, link to it:
    amended_by=models.IntegerField(null=True)
    


    #objects = ExpenditureManager()


    class Meta:
        ordering = ('-expenditure_date', )
        unique_together = (('image_number', 'transaction_id'), )

    def __unicode__(self):
        return str(self.image_number)
    
    def support_or_oppose(self):
        if self.support_oppose.upper() == 'S':
            return "Support"
        if self.support_oppose.upper() == 'O':
                return "Oppose"
        return "Unknown"

# Dump of transparency ids
class Transparency_Crosswalk(models.Model):
    year = models.IntegerField()
    td_name = models.CharField(max_length=255)
    td_id = models.CharField(max_length=32)
    fec_candidate_id = models.CharField(max_length=9)
    crp_candidate_id = models.CharField(max_length=9)
    
    def __unicode__(self):
        return self.td_name

# need a real loading process. To get 2012 used the below with a dump from ethan.
# load data infile '/Users/jfenton/unlimited_money_crash/transparency_data/td_crosswalk.csv'  into table rebuckley_transparency_crosswalk fields terminated by ',' ENCLOSED BY '"' ignore 1 lines (td_name, td_id, fec_candidate_id, crp_candidate_id);
#  update rebuckley_transparency_crosswalk set year = 2012;



class IEOnlyCommittee(models.Model):
    """For committees listed on this page: http://www.fec.gov/press/press2011/ieoc_alpha.shtml
    """
    fec_id = models.CharField(max_length=9, primary_key=True)
    committee_master_record=models.ForeignKey(Committee, null=True)
    display_name = models.CharField(max_length=100, null=True)
    slug = models.SlugField(null=True)
    fec_name = models.CharField(max_length=100, null=True)
    filing_freq_verbatim = models.CharField(max_length=100, null=True)
    # we can suck this in from the old pdf reading ap--without a start date I dunno how we total contributions.
    date_letter_submitted = models.DateField(null=True)
    # hand-enter this to link to sunlight reporting group's published profile
    profile_url = models.CharField(max_length=255, null=True, blank=True)
    # hand-enter this to link to a superpacs web site published profile
    superpac_url = models.CharField(max_length=255, null=True, blank=True)
    has_contributions = models.NullBooleanField(null=True, default=False)
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    # Only include independent expenditures in this total
    has_expenditures = models.NullBooleanField(null=True, default=False)
    total_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    # Include all spending reported on summary reports. Should this also include total_indy_expenditures after last report closing date?
    total_presidential_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_all_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)


    class Meta:
        ordering = ('-date_letter_submitted', )

    def __unicode__(self):
        return self.name
        
    def superpachackpage(self):
        return "/super-pacs/committee/%s/%s/" % (self.slug, self.fec_id)
        
# pac_candidate -- indicates a pac's total support or opposition towards a particular candidate. If a particular pac *both* supports and opposes a candidate, this should go in two separate entries. 
class Pac_Candidate(models.Model):
    committee = models.ForeignKey(Committee)
    candidate = models.ForeignKey(Candidate)
    support_oppose = models.CharField(max_length=1, 
                                       choices=(('S', 'Support'), ('O', 'Oppose'))
                                       )
    total_indepedent_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True) 
    
    
    class Meta:
        ordering = ('-total_indepedent_expenditures', )

    def __unicode__(self):
        return self.committee, self.candidate                                      