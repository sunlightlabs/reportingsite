import re

from django.db import models
from django.contrib.localflavor.us.us_states import STATE_CHOICES

STATE_CHOICES = dict(STATE_CHOICES)
# Create your models here.

form_types = [['F3X','Monthly/quarterly report'],
['F3P','Monthly/quarterly report'],
['F3L','Report of contributions bundled by lobbyist/registrants and lobbyist/registrant pacs'],
['F3','Monthly/quarterly report'],
['F99','Miscellaneous report'],
['F10','24-hour notice of expenditure from candidate\'s personal funds'],
['F13','Report of donations accepted for inaugural committee'],
['F1M','Notification of multicandidate status'],
['F1','Statement of organization'],
['F24','24/48 hr notice of independent/coordinated expenditures'],
['F2','Statement of candidacy'],
['F4','Report of receipts and disbursements - convention cmte'],
['F5','Report of independent expenditures made and contributions received'],
['F6','48-hour notice of contributions/loans received'],
['F7','Report of communication costs - corporations and membership orgs'],
['F8','Debt settlement plan'],
['F9','24-hour notice of disbursement/obligations for electioneering communications']]

type_hash={'C':'Communication Cost',
          'D': 'Delegate',
          'E': 'Electioneering Communication',
          'H': 'House',
          'I': 'Not a Committee',
          'N': 'Non-Party, Non-Qualified',
          'O': 'Super PAC',
          'P': 'Presidential',
          'Q': 'Qualified, Non-Party',
          'S': 'Senate',
          'U': 'Single candidate independent expenditure',
          'V': 'PAC with Non-Contribution Account - Nonqualified',
          'W': 'PAC with Non-Contribution Account - Qualified',
          'X': 'Non-Qualified Party',
          'Y': 'Qualified Party',
          'Z': 'National Party Organization',
          }

# whenever we run the scraper add it here. Periodically clear this out...
class Scrape_Time(models.Model):
    run_time = models.DateTimeField(auto_now=True)
    
    
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
    
    def race(self):
        
        if self.office == 'P':
            return 'President' 
        elif self.office == 'S' or self.district.startswith('S'):
            return '%s (Senate)' % self.fec_id[2:4]
        else:
            return '%s-%s (House)' % (self.fec_id[2:4], self.district.lstrip('0'))


# Populated from fec's committee master            
class Committee(models.Model):
    cycle = models.CharField(max_length=4)
    name = models.CharField(max_length=200)
    fec_id = models.CharField(max_length=9, blank=True)
    slug = models.SlugField(max_length=100)
    party = models.CharField(max_length=3, blank=True)
    # Josue Larose has 62 pacs and counting... 
    treasurer = models.CharField(max_length=90, blank=True, null=True)
    street_1 = models.CharField(max_length=34, blank=True, null=True)
    street_2 = models.CharField(max_length=34, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
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
                                       ('E', 'Electioneering Communication'),
                                       ('H', 'House'),
                                       ('I', 'Independent Expenditure (Not a Committee'),
                                       ('N', 'Non-Party, Non-Qualified'),
                                       ('O', 'Super PAC'),
                                       ('P', 'Presidential'),
                                       ('Q', 'Qualified, Non-Party'),
                                       ('S', 'Senate'),
                                       ('U', 'Single candidate independent expenditure'),
                                       ('V', 'PAC with Non-Contribution Account - Nonqualified'),
                                       ('W', 'PAC with Non-Contribution Account - Qualified'),
                                       ('X', 'Non-Qualified Party'),
                                       ('Y', 'Qualified Party'),
                                       ('Z', 'National Party Organization') ])

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
    connected_org_name=models.CharField(max_length=200, blank=True)
    candidate_id = models.CharField(max_length=9,blank=True)
    candidate_office = models.CharField(max_length=1, blank=True)
    
    # Fields set from fec lists after the fact
    is_superpac = models.NullBooleanField(null=True, default=False)    
    is_hybrid = models.NullBooleanField(null=True, default=False)  
    is_noncommittee = models.NullBooleanField(null=True, default=False)
    
    # related candidate, if there is one. From the candidate_id only. 
    related_candidate = models.ForeignKey(Candidate, null=True)
    # todo -- separate c4, c6, etc? 
    
    def get_fec_url(self):
        url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/" % (self.fec_id)
        return url
    
    def set_candidate(self):
        #print "committee id: %s candidate id %s" % (self.fec_id, self.candidate_id)
        try:
            this_candidate = Candidate.objects.get(fec_id=self.candidate_id)
            
            self.related_candidate = this_candidate
            self.save()
        except Candidate.DoesNotExist:
            #print "No match found"
            return
            
    def display_type(self):
        key = self.ctype
        try:
            return type_hash[key]
        except KeyError:
            return ''
    
# a local overlay.
class Committee_Overlay(models.Model):

    #what's the original record? This needs to work if there isn't one, so allow nulls. 
    committee_master_record=models.ForeignKey(Committee, null=True)

    cycle = models.CharField(max_length=4)

    # direct from the raw fec table
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, null=True)
    fec_id = models.CharField(max_length=9, blank=True)
    slug = models.SlugField(max_length=100)
    party = models.CharField(max_length=3, blank=True)
    treasurer = models.CharField(max_length=200, blank=True, null=True)
    street_1 = models.CharField(max_length=34, blank=True, null=True)
    street_2 = models.CharField(max_length=34, blank=True, null=True)
    city =models.CharField(max_length=30, blank=True, null=True)
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True, help_text='the state where the pac mailing address is')
    connected_org_name=models.CharField(max_length=200, blank=True)
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
    
    # total unitemized receipts
    total_unitemized = models.DecimalField(max_digits=19, decimal_places=2, null=True)
        
    # Only include independent expenditures in this total
    has_electioneering = models.NullBooleanField(null=True, default=False)
    has_independent_expenditures = models.NullBooleanField(null=True, default=False)
    
    
    total_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    # Include all spending reported on summary reports. Should this also include total_indy_expenditures after last report closing date?
    ie_support_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    ie_oppose_dems = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    ie_support_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    ie_oppose_reps = models.DecimalField(max_digits=19, decimal_places=2, null=True, default=0)
    
    
    total_presidential_indy_expenditures = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_electioneering = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    
    cash_on_hand = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cash_on_hand_date = models.DateField(null=True)

    # what kinda pac is it? 
    is_superpac = models.NullBooleanField(null=True, default=False)    
    is_hybrid = models.NullBooleanField(null=True, default=False)  
    is_noncommittee = models.NullBooleanField(null=True, default=False)

    
    org_status = models.CharField(max_length=31,
            choices=(('501(c)(4)', '501(c)(4)'),
                     ('501(c)(5)', '501(c)(5)'),
                     ('501(c)(6)', '501(c)(6)'),
                     ('527', '527'),
                     ('Private business', 'Private business'),
                     ('Public business', 'Public business'),
                     ('Individual', 'individual'),
            ),
            blank=True, null=True, help_text="We're only tracking these for non-committees")
    
    # what's their orientation
    political_orientation = models.CharField(max_length=1,null=True, choices=[
                            ('R', 'backs Republicans'),
                            ('D', 'backs Democrats'),
                            ('U', 'unknown'),
                            ('C', 'opposes incumbents--supports Tea Party'),
                          ])
    political_orientation_verified = models.BooleanField(default=False, help_text="Check this box if the political orientation is correct")
    
    designation = models.CharField(max_length=1,
                                      blank=False,
                                      null=True,
                                      choices=[('A', 'Authorized by Candidate'),
                                               ('J', 'Joint Fund Raiser'),
                                               ('P', 'Principal Committee of Candidate'),
                                               ('U', 'Unauthorized'),
                                               ('B', 'Lobbyist/Registrant PAC'),
                                               ('D', 'Leadership PAC')]
    )

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
                                     ('E', 'Electioneering Communication'),
                                     ('O', 'Super PAC') ])    


    class Meta:
        unique_together = (("cycle", "fec_id"),)
        ordering = ('-total_indy_expenditures', )

    def get_absolute_url(self):  
        return ("/outside-spenders/2014/committee/%s/%s/" % (self.slug, self.fec_id))
        
    def is_not_a_committee(self):
        if self.committee_master_record.ctype=='I':
            return True
        return False
    
    def neg_percent(self):
        if self.total_indy_expenditures == 0:
            return 0
        else:
            return 100*(self.ie_oppose_reps + self.ie_oppose_dems ) / self.total_indy_expenditures
    
    def pos_percent(self):
        if self.total_indy_expenditures == 0:
            return 0
        else:
            return 100*(self.ie_support_reps + self.ie_support_dems ) / self.total_indy_expenditures

        
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
        return "/outside-spenders/2014/csv/committee/%s/%s/" % (self.slug, self.fec_id) 

    def superpachackdonorscsv(self):
        return "/outside-spenders/2014/csv/contributions/%s/%s/" % (self.slug, self.fec_id)
        
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
               

            
    def display_type(self):
        key = self.ctype
        try:
            return type_hash[key]
        except KeyError:
            return ''
            
            
    def display_political_orientation(self):
        p = self.political_orientation
        if p=='D':
            return "Backs Democrats"
        if p=='R':
            return "Backs Republicans"
        else:
            return "Unassigned"


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
    
    # Is this candidate a winner in the general election?
    cand_is_gen_winner = models.NullBooleanField(null=True)
    # I = incumbent, O = Open seat, C=Challenger. Redistricting complicates this; they can both be incumbents. 
    cand_ici = models.CharField(max_length=1, blank=True, null=True)
    # Are they in the general election ? 
    is_general_candidate = models.NullBooleanField(null=True)
    ### data from the candidates own committees. Can be outta date for senate. From weball. 
    cand_ttl_receipts= models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_ending_cash = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_ttl_ind_contribs = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_cand_contrib = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_cand_loans = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_debts_owed_by = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    cand_report_date = models.DateField(null=True)
    
    
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


        return "/outside-spenders/2014/race_detail/%s/%s/%s/" % (office, state, district)                        

    def get_absolute_url(self):
        return "/outside-spenders/2014/candidate/%s/%s/" % (self.slug, self.fec_id)
        

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
        
        
    def influence_explorer_url(self):
        if not self.transparencydata_id:
            return None
        return 'http://influenceexplorer.com/politician/%s/%s' % (self.slug,
                                                                  self.transparencydata_id)        

class Filing_Header(models.Model):
    raw_filer_id=models.CharField(max_length=9, blank=True)
    form=models.CharField(max_length=7)
    # Is filing_number gonna be unique within a cycle? 
    filing_number=models.IntegerField(unique=True)
    version=models.CharField(max_length=7)

    coverage_from_date = models.DateField(null=True)
    coverage_through_date = models.DateField(null=True)

    # does this supercede another an filing?
    is_amendment=models.BooleanField()
    # if so, what's the original?
    amends_filing=models.IntegerField(null=True, blank=True)
    amendment_number = models.IntegerField(null=True, blank=True)

    # Is this filing superceded by another filing, either a later amendment, or a periodic filing.
    is_superceded=models.BooleanField(default=False)
    # which filing is this one superceded by? 
    amended_by=models.IntegerField(null=True, blank=True)

    # Is this a 24- or 48- hour notice that is now covered by a periodic (monthly/quarterly) filing, and if so, is ignorable ? 
    covered_by_periodic_filing=models.BooleanField(default=False)
    covered_by=models.IntegerField(null=True, blank=True)

    # When did the filing come in? 
    filing_time = models.DateTimeField(auto_now=False, null=True)
    # Is this an exact time, or is it a day estimated from the zip file directories ? 
    filing_time_is_exact = models.BooleanField()

    # Shortcut to store whether the files' been totally processed; helpful in tracking down filings where entry failed and they are now half done. 
    entry_complete = models.BooleanField(default=False)

    # store the actual header data as a fake hstore here:
    header_data = models.TextField(db_index=False)


    def __unicode__(self):
      return str(self.filing_number)

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
                                    choices=(('P', 'Primary'), ('G', 'General'), ('S', 'Special'), ('O', 'Other'), ('R', 'Runoff'), ('C', 'Convention'), ('E', 'Recount'))
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
    receipt_date = models.DateField(null=True)
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
    # If it's an amended version of an earlier filing, put the earlier filing here: 
    amends_filing=models.IntegerField(null=True) 
    # populated from the unprocessed_filing table.   
    process_time = models.DateTimeField(null=True) 

    
    filing_source = models.CharField(max_length=7, null=True, blank=True)
    # special flag to note that it's been amended by an F3X
    superceded_by_f3x=models.NullBooleanField(default=False)
    superceding_f3x=models.IntegerField(null=True)
    
    memo_code = models.CharField(max_length=100, blank=True)
    memo_text_description =  models.CharField(max_length=100, blank=True)
    


    class Meta:
        ordering = ('-expenditure_date', )
        unique_together = (('filing_number', 'transaction_id'), )

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
    entity_type = models.CharField(max_length=32)
    td_name = models.CharField(max_length=255)
    td_id = models.CharField(max_length=40)
    fec_candidate_id = models.CharField(max_length=9)
    crp_candidate_id = models.CharField(max_length=9)
    
    def __unicode__(self):
        return self.td_name

# need a real loading process. To get 2012 used the below with a dump from ethan.
#load data infile '...outside_spending/data/12/ie_crosswalk.csv'  into table outside_spending_transparency_crosswalk fields terminated by ',' ENCLOSED BY '"' ignore 1 lines (td_name, entity_type, td_id, fec_candidate_id, crp_candidate_id);
#update outside_spending_transparency_crosswalk set year = 2012;

#update outside_spending_candidate_overlay, outside_spending_transparency_crosswalk set outside_spending_candidate_overlay.crp_id = outside_spending_transparency_crosswalk.crp_candidate_id,  outside_spending_candidate_overlay.td_name=outside_spending_transparency_crosswalk.td_name , outside_spending_candidate_overlay.transparencydata_id =  outside_spending_transparency_crosswalk.td_id where  outside_spending_candidate_overlay.fec_id = outside_spending_transparency_crosswalk.fec_candidate_id;

# Sometimes the transparency ids have extra '-' in them. So run
#update outside_spending_candidate_overlay set transparencydata_id = replace(transparencydata_id, '-', '');

        
# pac_candidate -- indicates a pac's total support or opposition towards a particular candidate. If a particular pac *both* supports and opposes a candidate, this should go in two separate entries. 
class Pac_Candidate(models.Model):
    cycle = models.CharField(max_length=4, null=True, blank=True)
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
    cycle = models.CharField(max_length=4, null=True, blank=True)
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
    
    # summaries populated after the fact
    total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True)
#    contrib_date_approximate = models.DateField(null=True)
    general_ies = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_receipts_gen_candidates = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    percent_outside = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_pro_dem_general = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    total_pro_rep_general = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    winner = models.ForeignKey(Candidate_Overlay, null=True)
    is_freshman = models.NullBooleanField(null=True, blank=True)
    cook_rating = models.CharField(max_length=31, null=True, blank=True)

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
        return "/outside-spenders/2014/race_detail/%s/%s/%s/" % (self.office, self.state, self.district) 
        
class State_Aggregate(models.Model):    
    cycle = models.CharField(max_length=4, null=True, blank=True)
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
        return "/outside-spenders/2014/state/%s/" % (self.state)
        
#    def state_name(self):

# not used for 2014 ; there is some spending, but its minimal...
class President_State_Pac_Aggregate(models.Model):
    cycle = models.CharField(max_length=4, null=True, blank=True)
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
    cycle = models.CharField(max_length=4, null=True, blank=True)
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
    original=models.IntegerField(null=True)

    # alter table outside_spending_contribution add column original int;

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
            return "SA11AI Individual/Corporation"
        elif (self.line_type=='SA11C'):
            return "SA11C Political Action Committee"
        elif (self.line_type=='SA15'):
            return "SA15 Offsets To Operating Expenditure (line 15)"
        elif (self.line_type=='SA17'):
            return "SA17 Other Federal Receipts (Dividends, Interest, etc.)"
        elif (self.line_type=='SA13'):
            return "SA13 All Loans Received"
        elif (self.line_type=='SA12'):
            return "SA12 Transfers From Affiliated/Other Party Committees"            
        elif (self.line_type=='SA11B'):
            return "SA11B Political Party Committee"
        elif (self.line_type=='SA16'):
            return "SA16 Refunds of Contributions Made to Federal Candidates and Other Political Committees"
        elif (self.line_type=='SA14'):
            return "SA14 Loan Repayments Received"
        else:
            return None
            
    def contrib_asterisk(self):
        if (self.line_type=='SA15'):
            return "*" 
        else: 
            return ""


class Electioneering_94(models.Model):
    #electioneering=models.ForeignKey(Electioneering_93)
    cycle = models.CharField(max_length=4, null=True, blank=True)
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


            
class Electioneering_93(models.Model):
    cycle = models.CharField(max_length=4, null=True, blank=True)
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
    
    target = models.ManyToManyField(Electioneering_94, null=True)
    
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
    
    ## adding: 
    debts_owed = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    total_sched_e = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    
    ytd_total_receipts = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    ytd_total_disbursements = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    ytd_sched_e = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    
    ## New: 
    # Should we disregard this line item because it appears later in an amended filing?
    superceded_by_amendment=models.NullBooleanField(default=False, null=True)
    amends_earlier_filing = models.NullBooleanField(default=False, null=True)
    # if this entry is amended by a more recent entry, link to it:
    amended_by=models.IntegerField(null=True)
    original=models.IntegerField(null=True)
    
    ###
    #alter table `outside_spending_f3x_summary` add column `debts_owed` numeric(19, 2);
    #alter table `outside_spending_f3x_summary` add column `total_sched_e` numeric(19, 2);
    #alter table `outside_spending_f3x_summary` add column `ytd_total_receipts` numeric(19, 2);
    #alter table `outside_spending_f3x_summary` add column `ytd_total_disbursements` numeric(19, 2);
    #alter table `outside_spending_f3x_summary` add column `ytd_sched_e` numeric(19, 2);
    #alter table `outside_spending_f3x_summary` add column `superceded_by_amendment` bool;
    #alter table `outside_spending_f3x_summary` add column `amends_earlier_filing` bool;
    #alter table `outside_spending_f3x_summary` add column `amended_by` integer;
    #alter table `outside_spending_f3x_summary` add column `original` integer;
    ###
