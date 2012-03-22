from django.db import models
from django.contrib.localflavor.us.us_states import STATE_CHOICES

STATE_CHOICES = dict(STATE_CHOICES)
# Create your models here.

# whenever we run the scraper add it here. Periodically clear this out...
class Scrape_Time(models.Model):
    run_time = models.DateTimeField(auto_now=True)




# Populated from fec's committee master            
class Committee(models.Model):
    name = models.CharField(max_length=255)
    fec_id = models.CharField(max_length=9, blank=True)
    slug = models.SlugField(max_length=100)
    party = models.CharField(max_length=3, blank=True)
    # Josue Larose has 62 pacs and counting... 
    treasurer = models.CharField(max_length=38, blank=True, null=True)
    street_1 = models.CharField(max_length=34, blank=True, null=True)
    street_2 = models.CharField(max_length=34, blank=True, null=True)
    city =models.CharField(max_length=18, blank=True, null=True)
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    state_race = models.CharField(max_length=2, blank=True, null=True)
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
    
    # Fields set from fec lists after the fact
    is_superpac = models.NullBooleanField(null=True, default=False)    
    is_hybrid = models.NullBooleanField(null=True, default=False)  
    is_nonprofit = models.NullBooleanField(null=True, default=False)
    # todo -- separate c4, c6, etc? 
    
    
    
# a local overlay.
class Committee_Overlay(models.Model):

    #what's the original record? This needs to work if there isn't one, so allow nulls. 
    committee_master_record=models.ForeignKey(Committee, null=True)

    # should be 4-digit year here. 
    cycle=models.IntegerField()

    # direct from the raw fec table
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, null=True)
    fec_id = models.CharField(max_length=9, blank=True)
    slug = models.SlugField(max_length=100)
    party = models.CharField(max_length=3, blank=True)
    treasurer = models.CharField(max_length=38, blank=True, null=True)
    street_1 = models.CharField(max_length=34, blank=True, null=True)
    street_2 = models.CharField(max_length=34, blank=True, null=True)
    city =models.CharField(max_length=18, blank=True, null=True)
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    state_race = models.CharField(max_length=2, blank=True, null=True)
    connected_org_name=models.CharField(max_length=65, blank=True)
    filing_frequency = models.CharField(max_length=1, blank=True)

    candidate_id = models.CharField(max_length=9,blank=True)
    candidate_office = models.CharField(max_length=1, blank=True)    


    # hand-enter this to link to sunlight reporting group's published profile
    profile_url = models.CharField(max_length=255, null=True, blank=True, help_text="What's the url of sunlight's profile of this candidate? Please include the full link, i.e. http://sunlight/etc/etc.html. Leave blank if there isn't one")
    supporting = models.CharField(max_length=255, null=True, blank=True, help_text="Who is this PAC supporting?")
    # hand-enter this to link to a superpacs web site published profile
    superpac_url = models.CharField(max_length=255, null=True, blank=True, help_text="What's the super PAC's web site?")
    has_contributions = models.NullBooleanField(null=True, default=False)
    # total receipts
    total_contributions = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    # Only include independent expenditures in this total
    has_electioneering = models.NullBooleanField(null=True, default=False)
    has_independent_expenditures = models.NullBooleanField(null=True, default=False)
    
    
    total_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    # Include all spending reported on summary reports. Should this also include total_indy_expenditures after last report closing date?
    total_presidential_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cash_on_hand_date = models.DateField(null=True)

    # what kinda pac is it? 
    is_superpac = models.NullBooleanField(null=True, default=False)    
    is_hybrid = models.NullBooleanField(null=True, default=False)  
    is_c4 = models.NullBooleanField(null=True, default=False)


    class Meta:
        unique_together = (("cycle", "fec_id"),)
        ordering = ('-total_indy_expenditures', )

    def get_absolute_url(self):  
        return ("/outside-spending/committee/%s/%s/" % (self.slug, self.fec_id))

    def __unicode__(self):
        return self.name        
        
    def has_linkable_url(self):
        """Don't display a url if someone adds a space there... """
        if (len(self.profile_url.strip()) > 4):
            return True
        return False    
        
    def superpac_status(self):
        if (self.is_superpac):
            return 'Y'
        else:
            return 'N'    

    def hybrid_status(self):
        if (self.is_hybrid):
            return 'Y'
        else:
            return 'N'
            
    def superpachackcsv(self):
        return "/outside-spending/csv/committee/%s/%s/" % (self.slug, self.fec_id) 

    def superpachackdonorscsv(self):
        return "/outside-spending/csv/contributions/%s/%s/" % (self.slug, self.fec_id)
        
    def filing_frequency_text(self):
        if (self.filing_frequency.upper()=='M'):
            return "Monthly"
        if (self.filing_frequency.upper()=='Q'):
            return "Quarterly"
        if (self.filing_frequency.upper()=='T'):
            return "Terminated"
        if (self.filing_frequency.upper()=='W'):
            return "Waived"
        if (self.filing_frequency.upper()=='A'):
            return "Administratively Terminated"            
               

# populated from fec's candidate master
class Candidate(models.Model):
    cycle = models.CharField(max_length=4)
    fec_id = models.CharField(max_length=9, blank=True)
    fec_name = models.CharField(max_length=255) 
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
    # the state where the race is taking place (from the candidate id)
    state_race = models.CharField(max_length=2, blank=True, null=True) 
    campaign_com_fec_id = models.CharField(max_length=9, blank=True)


# a local overlay        
class Candidate_Overlay(models.Model):

    # copied from the raw fec model
    cycle = models.CharField(max_length=4)
    fec_id = models.CharField(max_length=9, blank=True)
    fec_name = models.CharField(max_length=255) 
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
    # state is from the candidate's address                                    
    state_address = models.CharField(max_length=2, blank=True)   
    district = models.CharField(max_length=2, blank=True)
    # the state where the race is taking place (from the candidate id)
    state_race = models.CharField(max_length=2, blank=True, null=True) 
    campaign_com_fec_id = models.CharField(max_length=9, blank=True)


    # add on id fields
    crp_id = models.CharField(max_length=9, blank=True, null=True)
    crp_name = models.CharField(max_length=255, blank=True, null=True)
    td_name = models.CharField(max_length=255, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True) 
    transparencydata_id = models.CharField(max_length=40, default='', null=True)    

    #

    slug = models.SlugField()
    total_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    # need to add electioneering here:
    electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    def __unicode__(self):
        return str(self.fec_name)
        
    def state(self):
        if self.office=='P':
            return 'NA'
        else:
            return self.state_race
            
    def race(self):
        if self.office == 'P':
            return 'President'
        elif self.office == 'S' or self.district.startswith('S'):
            return '%s (Senate)' % self.state()
        else:
            return '%s-%s (House)' % (self.state(), self.district.lstrip('0'))
            
            
    def get_race_url(self):
        office=self.office
        state=self.state_race
        district = self.district
        if (office == 'P'):
            state='00'
            district='00'
        elif (office=='S'):
            district='00'


        return "/outside-spending/race_detail/%s/%s/%s/" % (office, state, district)                        

    def get_absolute_url(self):
        return "/outside-spending/candidate/%s/%s/" % (self.slug, self.fec_id)
        

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
            
    def display_party(self):
        if (self.party.upper()=='REP'):
            return '(R)'
        elif (self.party.upper()=='DEM'):
            return '(D)'
        else: 
            return ''
        # todo--add other parties, if there are any that are being used? 
        
        

class Filing_Header(models.Model):
    raw_filer_id=models.CharField(max_length=9, blank=True)
    filer = models.ForeignKey(Committee_Overlay, null=True)
    form=models.CharField(max_length=7)
    filing_number=models.IntegerField(unique=True)
    
    # is this an amended filing?
    is_amendment=models.BooleanField()
    # if so, what's the original?
    amends_filing=models.IntegerField(null=True, blank=True)
    
    # Is this filing superceded by another filing?
    is_amended=models.BooleanField(default=False)
    # which filing is this one superceded by? 
    amended_by=models.IntegerField(null=True, blank=True)
    header_text=models.TextField()
    

# filings are unique by filing number and transaction id    
class Filing_Rows(models.Model):
    parent_filing=models.ForeignKey(Filing_Header)
    filer = models.ForeignKey(Committee_Overlay, null=True)
    filing_number=models.IntegerField()
    parent_form = models.CharField(max_length=7)
    superceded_by_amendment=models.BooleanField(default=False)
    line_type=models.CharField(max_length=15, blank=True)
    line_text=models.TextField()
    transaction_id = models.CharField(max_length=32)
    
    class Meta:
        unique_together = ("filing_number", "transaction_id")
        
        
# Add this so we don't have to join to committee overlay:
        
# old style expenditure -- load from bulk file. 


# This needs a 'final' -- i.e. unamended -- manager, but unclear if it should be on this model or a distillation
class Expenditure(models.Model):
    cycle = models.CharField(max_length=4, null=True)
    image_number = models.BigIntegerField()
    line_hash = models.BigIntegerField(null=True)
    raw_committee_id = models.CharField(max_length=9, null=True)
    committee = models.ForeignKey(Committee_Overlay, null=True)
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
    candidate = models.ForeignKey(Candidate_Overlay, blank=True, null=True) # NULL for electioneering
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


    # Put in this model so we don't have to join later.
    committee_name = models.CharField(max_length=255)
    
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
        
    def unmatched_amendment(self):
        if self.amendment.startswith('A') and self.amends_earlier_filing == False:
            return True
        else: 
            return False
    
    def race_name(self):
        if self.office == 'P':
            return 'President'
        elif self.office == 'S' or self.district.startswith('S'):
            return '%s (Senate)' % self.state()
        else:
            return '%s-%s (House)' % (self.state(), self.district.lstrip('0'))            

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




        
# pac_candidate -- indicates a pac's total support or opposition towards a particular candidate. If a particular pac *both* supports and opposes a candidate, this should go in two separate entries. 
class Pac_Candidate(models.Model):
    committee = models.ForeignKey(Committee_Overlay)
    candidate = models.ForeignKey(Candidate_Overlay)
    support_oppose = models.CharField(max_length=1, 
                                       choices=(('S', 'Support'), ('O', 'Oppose'))
                                       )
    total_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True) 
    total_ec = models.DecimalField(max_digits=19, decimal_places=2, null=True) 
    
    class Meta:
        ordering = ('-total_ind_exp', )

    def __unicode__(self):
        return self.committee, self.candidate
    
    def support_or_oppose(self):
        if (self.support_oppose.upper() == 'O'):
            return 'Oppose'
        elif (self.support_oppose.upper() == 'S'): 
            return 'Support'
        return ''
        
        
class Race_Aggregate(models.Model):
    office = models.CharField(max_length=1,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President')),
                              null=True
                              )    
    district = models.CharField(max_length=2, blank=True, null=True)
    # Null for president
    state = models.CharField(max_length=2, blank=True, null=True)
    expenditures_supporting = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True) 
    total_ec = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    class Meta:
        ordering = ('-total_ind_exp', )    
    
    def race_name(self):
        
        if self.office == 'P':
            return 'President'
        elif self.office == 'S':
            return '%s (Senate)' % self.state
        else:
            return '%s-%s (House)' % (self.state, self.district.lstrip('0')) 
            
    def get_absolute_url(self):
        return "/outside-spending/race_detail/%s/%s/%s/" % (self.office, self.state, self.district) 
        
class State_Aggregate(models.Model):
    state = models.CharField(max_length=2, blank=True, null=True)
    expenditures_supporting_president = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing_president = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_pres_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_supporting_house = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing_house = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_house_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)   
    expenditures_supporting_senate = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expenditures_opposing_senate = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_senate_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)     
    total_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    # last 10 days is recent
    recent_ind_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    recent_pres_exp = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_ec = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    def __unicode__(self):
        return STATE_CHOICES[self.state]
    
    def get_absolute_url(self):
        return "/outside-spending/state/%s/" % (self.state)
        
#    def state_name(self):


class President_State_Pac_Aggregate(models.Model):
    committee = models.ForeignKey(Committee_Overlay)
    candidate = models.ForeignKey(Candidate_Overlay)
    support_oppose = models.CharField(max_length=1, 
                                       choices=(('S', 'Support'), ('O', 'Oppose'))
                                       )    
    state = models.CharField(max_length=2, blank=True, null=True)
    expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    recent_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    def support_or_oppose(self):
        if (self.support_oppose.upper() == 'O'):
            return 'Oppose'
        elif (self.support_oppose.upper() == 'S'): 
            return 'Support'
        return ''    
        

class Contribution(models.Model):
    # the verbatim line type: should be SA 11A1/11B/11C entries 
    line_type = models.CharField(max_length=7)
    from_amended_filing = models.NullBooleanField()
    committee = models.ForeignKey(Committee_Overlay, null=True)
    committee_name = models.CharField(max_length=255)
    
    fec_committeeid = models.CharField(max_length=9)
    filing_number = models.IntegerField()
    transaction_id = models.CharField(max_length=32)
    back_ref_tran_id = models.CharField(max_length=32, blank=True)
    back_ref_sked_name = models.CharField(max_length=32, blank=True )
    entity_type = models.CharField(max_length=5, blank=True)
    display_name = models.CharField(max_length=255)

    contrib_org = models.CharField(max_length=200, blank=True)
    contrib_last = models.CharField(max_length=30, blank=True)
    contrib_first = models.CharField(max_length=20, blank=True)
    contrib_middle = models.CharField(max_length=20, blank=True)
    contrib_prefix = models.CharField(max_length=10, blank=True)
    contrib_suffix = models.CharField(max_length=10, blank=True)
    contrib_street_1 = models.CharField(max_length=34, blank=True)
    contrib_street_2 = models.CharField(max_length=34, blank=True)
    contrib_city = models.CharField(max_length=30, blank=True)
    contrib_state = models.CharField(max_length=2, blank=True)
    contrib_zip = models.CharField(max_length=10, blank=True)
    contrib_date = models.DateField(blank=True, null=True)
    contrib_amt = models.DecimalField(max_digits=19, decimal_places=2)
    contrib_agg = models.DecimalField(max_digits=19, decimal_places=2)
    contrib_purpose = models.CharField(max_length=100, blank=True)
    contrib_employer = models.CharField(max_length=38, blank=True)
    contrib_occupation = models.CharField(max_length=38, blank=True)
    memo_agg_item = models.CharField(max_length=100, blank=True)
    memo_text_descript = models.CharField(max_length=100, blank=True)

    url = models.URLField(verify_exists=False, null=True, blank=True)

    # Put the raw data line in here as ref--probably a good idea
    # data_row = models.TextField()

    # Should we disregard this line item because it appears later in an amended filing?
    superceded_by_amendment=models.BooleanField(default=False)
    amends_earlier_filing = models.BooleanField(default=False)
    # if this entry is amended by a more recent entry, link to it:
    amended_by=models.IntegerField(null=True)


    def __unicode__(self):
        return self.display_name

    class Meta:
        ordering = ('-contrib_amt', )
        
    def donor_display(self):
        if (self.contrib_org):
            return self.contrib_org
        else:
            return "%s, %s" % (self.contrib_last, self.contrib_first)
    
    def contrib_source(self):
        if (self.line_type=='SA11AI'):
            return "Individual/Corporation"
        elif (self.line_type=='SA11B'):
            return "Political Party Committee"
        elif (self.line_type=='SA11C'):
            return "Political Action Committee"
        elif (self.line_type=='SA15'):
            return "Offsets To Operating Expenditure (line 15)"
                                             
    def contrib_asterisk(self):
        if (self.line_type=='SA15'):
            return "*" 
        else: 
            return ""
            
class Electioneering_93(models.Model):
    exp_amo = models.DecimalField(max_digits=19, decimal_places=2)
    imageno = models.BigIntegerField()
    ele_yr = models.IntegerField()
    receipt_date = models.DateField(null=True)
    spe_nam = models.CharField(max_length=255, blank=True, null=True)
    payee = models.CharField(max_length=255, blank=True, null=True)
    purpose = models.CharField(max_length=255, blank=True, null=True)
    exp_date = models.DateField(null=True)
    transaction_id = models.CharField(max_length=32)
    filing_number = models.IntegerField()
    ele_typ = models.CharField(max_length=15)
    group_id = models.CharField(max_length=32, blank=True, null=True)
    fec_id = models.CharField(max_length=9)
    br_tran_id= models.CharField(max_length=32)
    amnd_ind= models.CharField(max_length=32)
    
    
    # Added on later by us: 
    superceded_by_amendment=models.BooleanField(default=False)
    committee = models.ForeignKey(Committee_Overlay, null=True)
    
    class Meta:
        unique_together = (("filing_number", "transaction_id"),)
    
    def __unicode__(self):
        return self.spe_nam, self.exp_amo, self.purpose
        
        
class Electioneering_94(models.Model):
    electioneering=models.ForeignKey(Electioneering_93)
    can_id = models.CharField(max_length=9)
    can_name = models.CharField(max_length=127)
    imageno = models.BigIntegerField()
    ele_yr = models.IntegerField()
    receipt_date = models.DateField(null=True)
    can_off = models.CharField(max_length=3, blank=True)
    can_state = models.CharField(max_length=2, blank=True, null=True)
    transaction_id = models.CharField(max_length=32)
    filing_number = models.IntegerField()
    ele_typ = models.CharField(max_length=15)
    group_id = models.CharField(max_length=32, blank=True, null=True)
    fec_id = models.CharField(max_length=9)
    br_tran_id= models.CharField(max_length=32)
    amnd_ind= models.CharField(max_length=32)
       
    
    
    # added:
    superceded_by_amendment=models.BooleanField(default=False)
    candidate=models.ForeignKey(Candidate_Overlay, null=True)
    
    
    class Meta:
        unique_together = (("filing_number", "transaction_id"),)
    
    def __unicode__(self):
        return self.spe_nam, self.exp_amo, self.purpose    
        
        
class F3X_Summary(models.Model):
    """The second line, aka 'form line' of a F3X filing"""
    filing_number = models.IntegerField()
    amended = models.NullBooleanField()
    committee_name = models.CharField(max_length=200)
    fec_id = models.CharField(max_length=9)
    address_change = models.CharField(max_length=1, blank=True)
    street_1 = models.CharField(max_length=34, blank=True)
    street_2 = models.CharField(max_length=34, blank=True)
    city = models.CharField(max_length=30, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip = models.CharField(max_length=10, blank=True)
    coverage_from_date = models.DateField(null=True, blank=True)
    coverage_to_date = models.DateField(null=True, blank=True)
    coh_begin = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    coh_close = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    itemized = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)

        