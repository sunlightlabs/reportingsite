from django.db import models
from outside_spending_2014.models import Committee_Overlay
import re

# SHOULD GO SOMEWHERE
CURRENT_CYCLE = '2014'

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

class Filing_Scrape_Time(models.Model):
    run_time = models.DateTimeField(auto_now=True)
    
    
# This is just to hold newly formed committees, scraped from a special page on the press site here: http://www.fec.gov/press/press2011/new_form1dt.shtml. Form F1's don't have to be filed electronically, so the press page appears to be the best resource out there. 
class newCommittee(models.Model):
    cycle = models.CharField(max_length=4, default=CURRENT_CYCLE)
    fec_id = models.CharField(max_length=9, blank=True, unique=True)
    ctype = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    date_filed = models.DateField()
    # is it in our system? 
    has_overlay = models.NullBooleanField(null=True)


    class Meta:
        ordering = ('-date_filed', )
        

    def __unicode__(self):
        return "%s formed %s" % (self.name, self.date_filed)
    

# Class to hold new filings, whether or not they've been parsed yet. 
class new_filing(models.Model):
    fec_id = models.CharField(max_length=9)
    committee_name = models.CharField(max_length=200)
    filing_number = models.IntegerField(primary_key=True)
    form_type = models.CharField(max_length=7)
    filed_date = models.DateField(null=True, blank=True)
    coverage_from_date = models.DateField(null=True, blank=True)
    coverage_to_date = models.DateField(null=True, blank=True)
    process_time = models.DateTimeField()
    is_superpac = models.NullBooleanField()
    related_committee = models.ForeignKey(Committee_Overlay, null=True)
    
    # have we processed this filing? 
    filing_is_parsed = models.NullBooleanField(default=False)
    
    ## summary data only available after form is parsed:
    
    # periodic reports only
    coh_start = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    coh_end = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    # Did they borrow *new* money this period ? 
    new_loans = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    
    # if applicable:
    tot_raised = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    tot_spent = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    
    def get_fec_url(self):
        url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/" % (self.fec_id, self.filing_number)
        return url
        
    def get_absolute_url(self):
        url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/%s/" % (self.fec_id, self.filing_number)
        return url
            
    def fec_all_filings(self):
        url = "http://query.nictusa.com/cgi-bin/dcdev/forms/%s/" % (self.fec_id)
        return url
        
    def get_form_name(self):
        amended = ""
        if re.search('A', self.form_type):
            amended="AMENDED "
        for f in form_types:
            if (re.match(f[0], self.form_type)):
                return amended + f[1]
        return ''

        
    class Meta:
        ordering = ('-date_filed', )


    def __unicode__(self):
        return "%s formed %s" % (self.name, self.date_filed)
    
class processing_memo(models.Model):
    message = models.CharField(max_length=127)
    value = models.IntegerField()
