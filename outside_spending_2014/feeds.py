from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404

from outside_spending_2014.models import Committee
from fec_alerts.models import new_filing, Filing_Scrape_Time


class FilingFeedBase(Feed):
    description_template = 'feeds/fec_filing_description.html'

    # What is this used for?
    def link(self, obj):
        return 'http://reporting.sunlightfoundation.com/outside-spenders/2014/super-pacs/'

    def description(self):
        return "Recent electronic campaign finance filings."
    
    def item_title(self, item):
        return  "FILING %s - %s" % (item.filing_number, item.get_form_name().upper() )
        
    def item_pubdate(self, item):
        return item.process_time

    def title(self):
        return "RECENT FILINGS FROM VARIOUS COMMITTEES"

class FilingFeed(FilingFeedBase): 
       
    def title(self, obj):
        return "%s - RECENT FILINGS" % obj.name
        
    def get_object(self, request, committee_id):
        return get_object_or_404(Committee, fec_id=committee_id) 
        
    def description(self, obj):
        return "Recent electronic campaign finance filings filed by %s" % (obj.name)             

    def items(self, obj):
        return new_filing.objects.filter(fec_id=obj.fec_id).order_by('-process_time')[:30]  

class CommitteeFormsFeed(FilingFeedBase): 
    form_list=[]

    def title(self, obj):
        return "%s - RECENT FORMS %s" % (obj.name, ", ".join(self.form_list) )

    def description(self, obj):
        return "Recent electronic campaign finance filings filed by %s" % (obj.name)        

    def get_object(self, request, committee_id, form_types):
        self.form_list=form_types.split("-")
        return get_object_or_404(Committee, fec_id=committee_id) 

    def items(self, obj):
        return new_filing.objects.filter(fec_id=obj.fec_id, form_type__in=self.form_list).order_by('-process_time')[:30]
    
class FilingsFeed(FilingFeedBase):
    committee_list=[]
    
    def get_object(self, request, committee_ids):
        self.committee_list = committee_ids.split("-")
        return Filing_Scrape_Time.objects.all().order_by('-run_time')[0]

    def items(self, obj):
        return new_filing.objects.filter(fec_id__in=self.committee_list).order_by('-process_time')[:30]

class FilingsFormFeed(FilingFeedBase):
    committee_list=[]
    form_list=[]

    def get_object(self, request, committee_ids, form_types):
        self.committee_list = committee_ids.split("-")
        self.form_list=form_types.split("-")
        return Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    
    def description(self):
        return "Recent electronic finance filings of forms: " + " ".join(self.form_list)

    def items(self, obj):
        return new_filing.objects.filter(fec_id__in=self.committee_list, form_type__in=self.form_list).order_by('-process_time')[:30]
        
class FilingsForms(FilingFeedBase):
    form_list=[]

    def get_object(self, request, form_types):
        self.form_list=form_types.split("-")
        return Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    
    def description(self):
        return "Recent electronic finance filings of forms: " + " ".join(self.form_list)

    def items(self, obj):
        return new_filing.objects.filter(form_type__in=self.form_list).order_by('-process_time')[:30]    
    
class SuperpacsForms(FilingFeedBase):
    form_list = []
    
    def get_object(self, request, form_types):
        self.form_list=form_types.split("-")
        return Filing_Scrape_Time.objects.all().order_by('-run_time')[0]
    
    def description(self):
        return "Superpac filings of forms: " + " ".join(self.form_list)

    def items(self, obj):
        return new_filing.objects.filter(form_type__in=self.form_list, is_superpac=True).order_by('-process_time')[:30]    
    
    def title(self, obj):
        return "Super PAC filings -- forms: " + " ".join(self.form_list)
    

